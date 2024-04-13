# Some test data for arm64 disassemblers

> To avoid using git LFS, the repo has the test set in a compressed form.
> To decompress the data, run the [prepare-once.py](./prepare-once.py)
> script.

To install the tools that generate the binary files:

```sh
cargo install disarm64
```

That allows to produce binary files for each instruction class, covering the
encoding space as the tools are told. The files inside the repo were produced
with no more than 0x10000 encodings per an instruction.

To generate disassembly diff's:

```sh
./gen-diff.py --help
```

```txt
usage: gen-diff.py [-h] [-f] [-n] [-t] [-v] [-d [{llvm,binutils,disarm64} ...]] [-j JOBS] [categories ...]

Generate disassembly listings, normalize them, and generate diffs for the specified categories

positional arguments:
  categories            Instruction categories to process, e.g., addsub_imm, addsub_shift, ...

options:
  -h, --help            show this help message and exit
  -f, --force           Regenerate the binaries and listings. Default: False, have to have the GNU binutils and LLVM installed.
  -n, --norm            Normalize disassembly.
  -t, --table           Produce the results as the markdown table.
  -v, --verbose         Enable verbose logging.
  -d [{llvm,binutils,disarm64} ...], --disasm [{llvm,binutils,disarm64} ...]
                        Disassembly tools to use, default: None
  -j JOBS, --jobs JOBS  Number of categories to process concurrently. Defaults to the number of CPU cores.
```

For example, after fixing the disassembler and installing it, can re-generate results for a specific
category:

```sh
./gen-diff.py addsub_ext -tnd disarm64
```

There are `117` categories for each of those a binary file with various encdodings is produced with `disarm64_gen`.
For the list of categories and number of encodings in the test set, please see the table below.

> This binary file [test0000.bin](./test/UBER/test0000.bin) has been derived from
> data in the [Binary Ninja ARM64 plugin](https://github.com/Vector35/arch-arm64)
> repo.

## Notes

- For `diff`-ing, the GNU diff is assumed.
- If you hae an IDE/text editor scanning for changes in this directory constantly, computing diff's might be slower.

## Statistics on diff's

This table shows how many encodings for the opcodes from the test set are formatted in a different way, and
the operand kinds for that formatting needs to be implemented to decrease the difference.

| Category | LLVM vs binutils | disarm64 vs binutils | Implement formatting for |
|----------|-----------------:|---------------------:|--------------------------|
| `aarch64_misc` | 111600/4161603 | **0**/4161603 | `` |
| `addsub_carry` | **0**/262144 | **0**/262144 | `` |
| `addsub_ext` | **0**/262144 | **0**/262144 | `` |
| `addsub_imm` | 12288/393216 | **0**/393216 | `` |
| `addsub_shift` | **0**/262144 | **0**/262144 | `` |
| `asimdall` | **0**/81920 | 55296/81920 | `` |
| `asimddiff` | **0**/3407872 | 2473984/3407872 | `` |
| `asimdelem` | **0**/2752512 | 2457600/2752512 | `em16`, `em`, `imm_rot2` |
| `asimdext` | **0**/65536 | 65536/65536 | `idx` |
| `asimdimm` | **0**/532480 | 532352/532480 | `sd`, `simd_imm`, `simd_imm_sft` |
| `asimdins` | **0**/360448 | 344064/360448 | `ed`, `en` |
| `asimdmisc` | **0**/430080 | 238592/430080 | `shll_imm` |
| `asimdperm` | **0**/393216 | 294912/393216 | `` |
| `asimdsame` | 262144/7536640 | 3360768/7536640 | `imm_rot1`, `imm_rot3`, `sd`, `sm`, `sn` |
| `asimdshf` | 6144/2752512 | 2752496/2752512 | `imm_vlsl`, `imm_vlsr`, `sd`, `simd_imm`, `simd_imm_sft` |
| `asimdtbl` | **0**/131072 | 131072/131072 | `lvn` |
| `asisddiff` | **0**/196608 | 196608/196608 | `sd`, `sm`, `sn` |
| `asisdelem` | **0**/983040 | 983040/983040 | `em16`, `em`, `sd`, `sn` |
| `asisdlse` | **0**/524288 | 524288/524288 | `lvt` |
| `asisdlsep` | **0**/524288 | 524288/524288 | `lvt`, `simd_addr_post` |
| `asisdlso` | **0**/557056 | 557056/557056 | `let`, `lvt_al` |
| `asisdlsop` | **0**/786432 | 786432/786432 | `let`, `lvt_al`, `simd_addr_post` |
| `asisdmisc` | **0**/120832 | 120832/120832 | `sd`, `sn` |
| `asisdone` | **0**/32768 | 32768/32768 | `en`, `sd` |
| `asisdpair` | **0**/19456 | 16384/19456 | `sd` |
| `asisdsame` | **0**/1933312 | 1933312/1933312 | `sd`, `sm`, `sn` |
| `asisdshf` | **0**/1835008 | 1835008/1835008 | `imm_vlsl`, `imm_vlsr`, `sd`, `sn` |
| `bfloat16` | **0**/297984 | 163840/297984 | `em16` |
| `bitfield` | **0**/196608 | 50988/196608 | `` |
| `branch_imm` | **0**/131072 | **0**/131072 | `` |
| `branch_reg` | **0**/4326 | **0**/4326 | `` |
| `compbranch` | **0**/131072 | **0**/131072 | `` |
| `condbranch` | **0**/131072 | **0**/131072 | `` |
| `condcmp_imm` | 16384/131072 | **0**/131072 | `` |
| `condcmp_reg` | 16384/131072 | **0**/131072 | `` |
| `condsel` | 32768/262144 | 5376/262144 | `` |
| `cryptoaes` | **0**/4096 | **0**/4096 | `` |
| `cryptosha2` | **0**/102400 | **0**/102400 | `` |
| `cryptosha3` | **0**/458752 | 65536/458752 | `imm` |
| `cryptosm3` | **0**/393216 | 262144/393216 | `em` |
| `cryptosm4` | **0**/33792 | **0**/33792 | `` |
| `cssc` | **0**/530432 | **0**/530432 | `` |
| `dotproduct` | **0**/458752 | 425984/458752 | `em` |
| `dp_1src` | **0**/19776 | **0**/19776 | `` |
| `dp_2src` | 1024/819200 | 264192/819200 | `` |
| `dp_3src` | **0**/458752 | 12288/458752 | `` |
| `exception` | **0**/589824 | **0**/589824 | `` |
| `extract` | **0**/41728 | **0**/41728 | `` |
| `float2fix` | **0**/524288 | **0**/524288 | `` |
| `float2int` | **0**/146432 | 6144/146432 | `vdd1`, `vnd1` |
| `floatccmp` | 28672/262144 | **0**/262144 | `` |
| `floatcmp` | **0**/20480 | **0**/20480 | `` |
| `floatdp1` | **0**/80896 | 11264/80896 | `` |
| `floatdp2` | **0**/884736 | **0**/884736 | `` |
| `floatdp3` | **0**/524288 | **0**/524288 | `` |
| `floatimm` | **0**/40960 | **0**/40960 | `` |
| `floatsel` | 14336/131072 | **0**/131072 | `` |
| `gcs` | **0**/2180 | **0**/2180 | `` |
| `ic_system` | 1967/492872 | 2702/492872 | `sme_sm_za` |
| `ldst_imm10` | 64/131072 | **0**/131072 | `` |
| `ldst_imm9` | **0**/983040 | **0**/983040 | `` |
| `ldst_pos` | **0**/786432 | **0**/786432 | `` |
| `ldst_regoff` | **0**/786432 | **0**/786432 | `` |
| `ldst_unpriv` | **0**/589824 | **0**/589824 | `` |
| `ldst_unscaled` | **0**/1966080 | **0**/1966080 | `` |
| `ldstexcl` | **0**/556032 | **0**/556032 | `` |
| `ldstnapair_offs` | **0**/262144 | **0**/262144 | `` |
| `ldstpair_indexed` | 11776/393216 | 11776/393216 | `` |
| `ldstpair_off` | 2048/393216 | 2048/393216 | `` |
| `loadlit` | **0**/262144 | **0**/262144 | `` |
| `log_imm` | **0**/262144 | **0**/262144 | `` |
| `log_shift` | **0**/524288 | **0**/524288 | `` |
| `lse128_atomic` | 24192/393216 | **0**/393216 | `` |
| `lse_atomic` | 42240/5572608 | **0**/5572608 | `` |
| `movewide` | 16383/196608 | **0**/196608 | `` |
| `pcreladdr` | **0**/131072 | **0**/131072 | `` |
| `rcpc3` | 176137/274432 | 274432/274432 | `let`, `rcpc3_addr_offset`, `rcpc3_addr_opt_postind`, `rcpc3_addr_opt_preind_wb`, `rcpc3_addr_postind`, `rcpc3_addr_preind_wb` |
| `sme2_mov` | **0**/3072 | 3072/3072 | `sme_za_array_off3_0`, `sme_za_array_off3_5`, `sme_zdnx2`, `sme_zdnx4`, `sme_znx2`, `sme_znx4` |
| `sme2_movaz` | 5376/5376 | 5376/5376 | `sme_za_array_vrsb_1`, `sme_za_array_vrsb_2`, `sme_za_array_vrsd_1`, `sme_za_array_vrsd_2`, `sme_za_array_vrsh_1`, `sme_za_array_vrsh_2`, `sme_za_array_vrss_1`, `sme_za_array_vrss_2`, `sme_zdnx2`, `sme_zdnx4` |
| `sme_fp_sd` | 30720/175104 | 175104/175104 | `sme_za_array_off3_0`, `sme_zm`, `sme_zmx2`, `sme_zmx4`, `sme_znx2`, `sme_znx4`, `sve_znxn` |
| `sme_int_sd` | 212992/498688 | 498688/498688 | `sme_za_array_off1x4`, `sme_za_array_off2x4`, `sme_za_array_off3_0`, `sme_zm`, `sme_zmx2`, `sme_zmx4`, `sme_znx2`, `sme_znx4`, `sve_zn`, `sve_znxn` |
| `sme_ldr` | **0**/2048 | 2048/2048 | `sme_addr_ri_u4xvl`, `sme_za_array_off4` |
| `sme_misc` | 2334884/5654465 | 5588929/5654465 | `sme_list_of_64bit_tiles`, `sme_pm`, `sme_shrimm4`, `sme_za_array_off1x4`, `sme_za_array_off2x2`, `sme_za_array_off2x4`, `sme_za_array_off3_0`, `sme_za_array_off3x2`, `sme_zada_2b`, `sme_zada_3b`, `sme_zdnx2`, `sme_zdnx4`, `sme_zm`, `sme_zm_index1`, `sme_zm_index2`, `sme_zm_index3_10`, `sme_zm_index3_1`, `sme_zm_index3_2`, `sme_zm_index4_10`, `sme_zm_index4_1`, `sme_zmx2`, `sme_zmx4`, `sme_znx2`, `sme_znx4`, `sme_zt0`, `sme_zt0_index`, `sme_zt0_list`, `sve_pg3`, `sve_simm6`, `sve_zd`, `sve_zm_16`, `sve_zn`, `sve_znxn` |
| `sme_mov` | **0**/262144 | 262144/262144 | `sme_za_hv_idx_dest`, `sme_za_hv_idx_src`, `sve_pg3`, `sve_zd`, `sve_zn` |
| `sme_psel` | **0**/131072 | 131072/131072 | `sme_pnt_wm_imm`, `sve_pnd`, `sve_png4_10` |
| `sme_shift` | **0**/196608 | 196608/196608 | `sme_shrimm5`, `sme_znx4`, `sve_zd` |
| `sme_size_12_bhs` | **0**/126976 | 126976/126976 | `sme_zdnx2`, `sme_zdnx4`, `sme_zn_index2_15`, `sme_zn_index2_16`, `sme_zn_index3_14`, `sme_zn_index3_15`, `sme_zn_index4_14`, `sme_zt0`, `sve_zd` |
| `sme_size_12_hs` | **0**/2048 | 2048/2048 | `sme_zdnx4`, `sme_zn_index1_16`, `sme_zt0` |
| `sme_size_22` | 93504/1249568 | 1249568/1249568 | `sme_pdx2`, `sme_pdxn`, `sme_pnd3`, `sme_png3`, `sme_pnn3_index1`, `sme_pnn3_index2`, `sme_pnn`, `sme_vlxn_10`, `sme_vlxn_13`, `sme_za_hv_idx_destxn`, `sme_za_hv_idx_srcxn`, `sme_zdnx2`, `sme_zdnx4`, `sme_zm`, `sme_zmx2`, `sme_zmx4`, `sme_znx2`, `sme_znx4`, `sve_pd`, `sve_zm_16`, `sve_zn` |
| `sme_size_22_hsd` | 31040/180224 | 180224/180224 | `sme_zdnx2`, `sme_zdnx4`, `sme_zm`, `sme_zmx2`, `sme_zmx4`, `sme_znx2`, `sve_zd`, `sve_zm_16`, `sve_zn` |
| `sme_start` | **0**/9 | 7/9 | `sme_sm_za` |
| `sme_stop` | **0**/9 | 7/9 | `sme_sm_za` |
| `sme_str` | **0**/2048 | 2048/2048 | `sme_addr_ri_u4xvl`, `sme_za_array_off4` |
| `sme_sz_23` | **0**/3072 | 3072/3072 | `sme_znx4`, `sve_zd` |
| `sve2_urqvs` | **0**/393216 | 393216/393216 | `sve_pg3`, `sve_zn` |
| `sve_cpy` | 20512/65536 | 65536/65536 | `sve_asimm`, `sve_pg4_16`, `sve_zd` |
| `sve_index` | **0**/65536 | 65536/65536 | `sve_zd`, `sve_zn_index` |
| `sve_index1` | 30720/32768 | 32768/32768 | `sve_zd`, `sve_zn_5_index` |
| `sve_limm` | **0**/262144 | 262144/262144 | `sve_limm`, `sve_zd` |
| `sve_misc` | 65542/16777768 | 16777767/16777768 | `sme_png3`, `sme_za_hv_idx_ldstr`, `sme_zdnx2`, `sme_zdnx4`, `sme_znx2`, `sme_znx4`, `sme_zt2`, `sme_zt3`, `sme_zt4`, `sme_ztx2_strided`, `sme_ztx4_strided`, `sve_addr_r`, `sve_addr_ri_s4x16`, `sve_addr_ri_s4x2xvl`, `sve_addr_ri_s4x32`, `sve_addr_ri_s4x3xvl`, `sve_addr_ri_s4x4xvl`, `sve_addr_ri_s4xvl`, `sve_addr_ri_s6xvl`, `sve_addr_ri_s9xvl`, `sve_addr_ri_u6`, `sve_addr_ri_u6x2`, `sve_addr_ri_u6x4`, `sve_addr_ri_u6x8`, `sve_addr_rr`, `sve_addr_rr_lsl1`, `sve_addr_rr_lsl2`, `sve_addr_rr_lsl3`, `sve_addr_rr_lsl4`, `sve_addr_rx`, `sve_addr_rx_lsl1`, `sve_addr_rx_lsl2`, `sve_addr_rx_lsl3`, `sve_addr_rz`, `sve_addr_rz_lsl1`, `sve_addr_rz_lsl2`, `sve_addr_rz_lsl3`, `sve_addr_rz_xtw1_14`, `sve_addr_rz_xtw1_22`, `sve_addr_rz_xtw2_14`, `sve_addr_rz_xtw2_22`, `sve_addr_rz_xtw3_14`, `sve_addr_rz_xtw3_22`, `sve_addr_rz_xtw_14`, `sve_addr_rz_xtw_22`, `sve_addr_zi_u5`, `sve_addr_zi_u5x2`, `sve_addr_zi_u5x4`, `sve_addr_zi_u5x8`, `sve_addr_zx`, `sve_addr_zz_sxtw`, `sve_addr_zz_uxtw`, `sve_imm_rot2`, `sve_pattern_scaled`, `sve_pd`, `sve_pg3`, `sve_pg4_10`, `sve_pg4_5`, `sve_pm`, `sve_pn`, `sve_pnd`, `sve_pnt`, `sve_prfop`, `sve_simm6`, `sve_uimm8_53`, `sve_zd`, `sve_zm3_11_index`, `sve_zm3_19_index`, `sve_zm3_22_index`, `sve_zm3_index`, `sve_zm4_11_index`, `sve_zm4_index`, `sve_zm_16`, `sve_zm_5`, `sve_zm_imm4`, `sve_zn`, `sve_znxn`, `sve_zt`, `sve_ztxn` |
| `sve_movprfx` | **0**/65536 | 65536/65536 | `sve_pg3`, `sve_zd`, `sve_zn` |
| `sve_pred_zm` | **0**/16384 | 16384/16384 | `sve_pd`, `sve_pg4_10`, `sve_pn` |
| `sve_shift_pred` | **0**/294912 | 294912/294912 | `sve_pg3`, `sve_shlimm_pred`, `sve_shrimm_pred`, `sve_zd` |
| `sve_shift_tsz_bhsd` | **0**/458752 | 458752/458752 | `sve_shlimm_unpred`, `sve_shrimm_unpred`, `sve_zd`, `sve_zn` |
| `sve_shift_tsz_hsd` | **0**/1310720 | 1310720/1310720 | `sve_shlimm_unpred_22`, `sve_shrimm_unpred_22`, `sve_zd`, `sve_zn` |
| `sve_shift_unpred` | **0**/196608 | 196608/196608 | `sve_shlimm_unpred`, `sve_shrimm_unpred`, `sve_zd`, `sve_zn` |
| `sve_size_13` | **0**/131072 | 131072/131072 | `sve_zd`, `sve_zm_16`, `sve_zn` |
| `sve_size_bh` | **0**/131072 | 131072/131072 | `sve_pd`, `sve_pg3`, `sve_zm_16`, `sve_zn` |
| `sve_size_bhs` | **0**/983040 | 983040/983040 | `sve_pd`, `sve_pg3`, `sve_vd`, `sve_zd`, `sve_zm_16`, `sve_zm_5`, `sve_zn` |
| `sve_size_bhsd` | 20512/8710144 | 8710144/8710144 | `simm5`, `sve_aimm`, `sve_asimm`, `sve_imm_rot2`, `sve_imm_rot3`, `sve_pattern`, `sve_pd`, `sve_pg3`, `sve_pg4_10`, `sve_pg4_5`, `sve_pm`, `sve_pn`, `sve_simm5`, `sve_simm5b`, `sve_simm8`, `sve_uimm7`, `sve_uimm8`, `sve_vd`, `sve_vm`, `sve_vn`, `sve_za_5`, `sve_zd`, `sve_zm_16`, `sve_zm_5`, `sve_zn`, `sve_znxn` |
| `sve_size_hsd` | **0**/6774784 | 6774784/6774784 | `imm_rot2`, `sve_i1_half_one`, `sve_i1_half_two`, `sve_i1_zero_one`, `sve_imm_rot1`, `sve_pd`, `sve_pg3`, `sve_pg4_16`, `sve_pg4_5`, `sve_uimm3`, `sve_vd`, `sve_za_16`, `sve_zd`, `sve_zm_16`, `sve_zm_5`, `sve_zn` |
| `sve_size_hsd2` | **0**/32768 | 32768/32768 | `sve_pg3`, `sve_zd`, `sve_zn` |
| `sve_size_sd` | **0**/724992 | 722944/724992 | `sve_addr_zz_lsl`, `sve_imm_rot2`, `sve_pg3`, `sve_zd`, `sve_zm_16`, `sve_zm_5`, `sve_zn` |
| `sve_size_sd2` | 4096/131072 | 131072/131072 | `sve_addr_zx`, `sve_pg3`, `sve_ztxn` |
| `sve_size_tsz_bhs` | **0**/49152 | 49152/49152 | `sve_zd`, `sve_zn` |
| `testbranch` | **0**/131072 | **0**/131072 | `` |
| `the` | 48384/2097152 | **0**/2097152 | `` |
