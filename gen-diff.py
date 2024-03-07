#!/usr/bin/env python3
__doc__ = """
Generate disassembly listings, normalize them, and generate diffs for the specified categories
"""

import logging
import os
import subprocess
import re

from concurrent.futures import ThreadPoolExecutor, as_completed

log = logging.getLogger("gen-diff")
log_format = "[%(asctime)s][%(levelname)-8s][%(name)-8s] %(message)s"

def count_lines(filepath):
    with open(filepath, 'r') as file:
        return sum(1 for _ in file)

def find_unhandled_operands(filepath):
    with open(filepath, 'r') as file:
        content = file.read()
    # Find strings that start and end with a colon
    matches = re.findall(r":\w+:", content)
    return ",".join(sorted(set(matches))).replace(":", "")

def run_command(command, stdout=None, shell=False):
    log.debug(f"Running command: {command}")
    command = command.split()
    subprocess.run(command, shell=shell, stdout=stdout)

# GNU diff command configuration
DIFF = "diff -waybB --speed-large-files --strip-trailing-cr --horizon-lines=0 --suppress-common-lines"

# Paths to the norm binary
NORM = "./target/release/norm"

DEFAULT_CATEGORIES = set([
    "aarch64_misc", "addsub_carry", "addsub_ext", "addsub_imm", "addsub_shift", "asimdall", "asimddiff", "asimdelem", 
    "asimdext", "asimdimm", "asimdins", "asimdmisc", "asimdperm", "asimdsame", "asimdshf", "asimdtbl", "asisddiff", 
    "asisdelem", "asisdlse", "asisdlsep", "asisdlso", "asisdlsop", "asisdmisc", "asisdone", "asisdpair", "asisdsame", 
    "asisdshf", "bfloat16", "bitfield", "branch_imm", "branch_reg", "compbranch", "condbranch", "condcmp_imm", 
    "condcmp_reg", "condsel", "cryptoaes", "cryptosha2", "cryptosha3", "cryptosm3", "cryptosm4", "cssc", "dotproduct", 
    "dp_1src", "dp_2src", "dp_3src", "exception", "extract", "float2fix", "float2int", "floatccmp", "floatcmp", "floatdp1", 
    "floatdp2", "floatdp3", "floatimm", "floatsel", "gcs", "ic_system", "ldst_imm10", "ldst_imm9", "ldst_pos", 
    "ldst_regoff", "ldst_unpriv", "ldst_unscaled", "ldstexcl", "ldstnapair_offs", "ldstpair_indexed", "ldstpair_off", 
    "loadlit", "log_imm", "log_shift", "lse_atomic", "lse128_atomic", "movewide", "pcreladdr", "rcpc3", "sme_fp_sd", 
    "sme_int_sd", "sme_ldr", "sme_misc", "sme_mov", "sme_psel", "sme_shift", "sme_size_12_bhs", "sme_size_12_hs", 
    "sme_size_22_hsd", "sme_size_22", "sme_start", "sme_stop", "sme_str", "sme_sz_23", "sme2_mov", "sme2_movaz", "sve_cpy", 
    "sve_index", "sve_index1", "sve_limm", "sve_misc", "sve_movprfx", "sve_pred_zm", "sve_shift_pred", "sve_shift_tsz_bhsd", 
    "sve_shift_tsz_hsd", "sve_shift_unpred", "sve_size_13", "sve_size_bh", "sve_size_bhs", "sve_size_bhsd", "sve_size_hsd", 
    "sve_size_hsd2", "sve_size_sd", "sve_size_sd2", "sve_size_tsz_bhs", "sve2_urqvs", "testbranch", "the"
])

def process_category(category, generate_binaries=True, normalize_disasm=True, disasm=set()):
    if category not in DEFAULT_CATEGORIES:
        log.warning(f"Category {category} is not in the default set of categories")
        return

    log.info(f"Processing {category}")

    dir_path = f"./test/classes/{category}"
    os.makedirs(dir_path, exist_ok=True)

    llvm_lst = f"{dir_path}/{category}-llvm.lst"
    binutils_lst = f"{dir_path}/{category}-binutils.lst"
    disarm64_lst = f"{dir_path}/{category}-disarm64.lst"
    
    llvm_lst_norm = f"{dir_path}/{category}-llvm.norm.lst"
    binutils_lst_norm = f"{dir_path}/{category}-binutils.norm.lst"
    disarm64_lst_norm = f"{dir_path}/{category}-disarm64.norm.lst"

    # Generate binary, ELF, and listing files
    if generate_binaries:
        log.info(f"Generating {dir_path}/{category}.bin")
        run_command(f"disarm64_gen ./aarch64.json -c {category} -t {dir_path}/{category}.bin")

        log.info(f"Generating {dir_path}/{category}.elf")
        run_command(f"rust-objcopy -I binary -O elf64-littleaarch64 --rename-section=.data=.text,code {dir_path}/{category}.bin {dir_path}/{category}.elf")

    # Generate disassembly listings
    if 'llvm' in disasm:
        log.info(f"Generating {llvm_lst}")
        with open(llvm_lst, "w") as outfile:
            run_command(f"rust-objdump -d {dir_path}/{category}.elf", stdout=outfile)

    if 'binutils' in disasm:
        log.info(f"Generating {binutils_lst}")
        with open(binutils_lst, "w") as outfile:
            run_command(f"aarch64-linux-gnu-objdump -m aarch64 -b binary -D {dir_path}/{category}.bin", stdout=outfile)

    if 'disarm64' in disasm:
        log.info(f"Generating {disarm64_lst}")
        with open(disarm64_lst, "w") as outfile:
            run_command(f"disarm64 bin {dir_path}/{category}.bin", stdout=outfile)

    # Normalize disassembly listings
    if normalize_disasm:
        for lst in [llvm_lst, binutils_lst, disarm64_lst]:
            norm_lst = lst.replace(".lst", ".norm.lst")
            log.info(f"Generating normalized disassembly for {category}: {norm_lst}")
            with open(norm_lst, "w") as outfile:
                run_command(f"{NORM} {lst}", stdout=outfile)

    # Generate diffs
    for lst_norm in [llvm_lst_norm, disarm64_lst_norm]:
        diff_file = lst_norm.replace(".norm.lst", ".diff")
        log.info(f"Generating diffs against binutils for {category}: {diff_file}")
        with open(diff_file, "w") as outfile:
            run_command(f"{DIFF} {lst_norm} {binutils_lst_norm}", stdout=outfile)

    # Count stats and look for unhandled operands
    log.info(f"Counting stats for {category}")
    stats = {
        "llvm": count_lines(llvm_lst_norm),
        "binutils": count_lines(binutils_lst_norm),
        "disarm64": count_lines(disarm64_lst_norm),
        "llvm_binutils_diff": count_lines(f"{dir_path}/{category}-llvm.diff"),
        "disarm64_binutils_diff": count_lines(f"{dir_path}/{category}-disarm64.diff")
    }

    stats_msg = f"{stats['llvm_binutils_diff']}/{stats['llvm']} {stats['disarm64_binutils_diff']}/{stats['disarm64']}"
    with open(f"{dir_path}/{category}.stats", "w") as stats_file:
        stats_file.write(stats_msg)
    log.info("Stats: " + stats_msg)

    log.info(f"Looking for the operands unhandled by disarm64 for {category}")
    unhandled_operands = find_unhandled_operands(disarm64_lst_norm)
    with open(f"{dir_path}/{category}-disarm64.unhandled", "w") as unhandled_file:
        unhandled_file.write(unhandled_operands)
    log.info(f"Unhandled operands: {unhandled_operands}")

    log.info(f"Done with {category}")

def generate_stats_table(categories):
    log.info("Generating stats table")

    table = "| Category | LLVM vs binutils | disarm64 vs binutils | Implement formatting for |\n"
    table += "|----------|-----------------:|---------------------:|--------------------------|\n"
    for category in sorted(categories):
        dir_path = f"./test/classes/{category}"
        stats_file = f"{dir_path}/{category}.stats"
        unhandled_file = f"{dir_path}/{category}-disarm64.unhandled"
        with open(stats_file, "r") as file:
            stats = file.read()
            stats = " | ".join(stats.split())
        with open(unhandled_file, "r") as file:
            unhandled = file.read()
            unhandled = unhandled.replace(",", "`, `")
        table += f"| `{category}` | {stats} | `{unhandled}` |\n"
    return table

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-f", "--force", action="store_true", help="Regenerate the binaries and listings. Default: False, have to have the GNU binutils and LLVM installed.")
    parser.add_argument("-n", "--norm", action="store_true", help="Normalize disassembly.")
    parser.add_argument("-t", "--table", action="store_true", help="Produce the results as the markdown table.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("-d", "--disasm", nargs="*", choices=["llvm", "binutils", "disarm64"], default=[], help="Disassembly tools to use, default: None")
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count(), help="Number of categories to process concurrently. Defaults to the number of CPU cores.")
    parser.add_argument("categories", nargs="*", help="Instruction categories to process, e.g., addsub_imm, addsub_shift, ...")
    args = parser.parse_args()

    categories = set(args.categories)
    if not categories:
        categories = DEFAULT_CATEGORIES

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format=log_format)

    norm = args.norm
    if norm:
        run_command(f"cargo build --release")
    disasm = set(args.disasm)

    log.info(f"Processing categories: {categories}")
    log.info(f"Concurrently processing {args.jobs} categories")

    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        future_to_category = {
            executor.submit(
                process_category, 
                category,
                generate_binaries=args.force, normalize_disasm=norm, disasm=disasm
            ): category for category in sorted(categories)
        }
        
        for future in as_completed(future_to_category):
            category = future_to_category[future]
            try:
                future.result()
            except Exception as exc:
                log.error(f"{category} generated an exception: {exc}")

    if args.table:
        print(generate_stats_table(categories))
