//! This program reads a disassembly file and prints the opcodes, mnemonics, and operands.
//!
//! It attempts to "normalize" the output to some common form; a very not perfect attempt
//! because it does not have the context of the instruction set. E.g. "mov's" are normalized
//! in a very specific way.
//! Nonetheless, it is useful for a quick look at the differences between two assembly files.
//! The output is Not suitable for machine analysis.

use std::env;
use std::fs::File;
use std::io;
use std::io::BufRead;
use std::io::BufReader;

// Without the context, showing whether the number 32-bit or 64-bit is
// it is not obvious how to to be absolutely precise with the negative numbers.
// Thus there will be some junk in the output.
fn try_hex(s: &str) -> String {
    const SUFFIXES: &[&str] = &[",", ")", "]", "]!"];
    if !s.starts_with('#') {
        return s.to_string();
    }

    let num_start = 1;
    let mut num_suffix = "";
    for suffix in SUFFIXES {
        if s.ends_with(suffix) {
            num_suffix = suffix;
            break;
        }
    }
    let suffix = num_suffix;
    let num_end = s.len() - suffix.len();

    let num = &s[num_start..num_end];
    if num.starts_with("0x") {
        if let Ok(num) = u32::from_str_radix(&num[2..], 16) {
            return format!("#{:#x}{}", num, suffix);
        }
        if let Ok(num) = u64::from_str_radix(&num[2..], 16) {
            return format!("#{:#x}{}", num, suffix);
        }
    } else if num.starts_with("-0x") {
        if let Ok(num) = u32::from_str_radix(&num[3..], 16) {
            return format!("#{:#x}{}", (!num).wrapping_add(1), suffix);
        }
        if let Ok(num) = u64::from_str_radix(&num[3..], 16) {
            return format!("#{:#x}{}", (!num).wrapping_add(1), suffix);
        }
    } else if num.contains('.') || num.contains("e+") || num.contains("e-") {
        let f = num.parse::<f64>().unwrap();
        if f.fract() != 0.0 {
            return format!("#{}{}", f, suffix);
        } else {
            return format!("#{:#x}{}", f as i32, suffix);
        }
    } else if num.starts_with('-') {
        if let Ok(num) = u32::from_str_radix(&num[1..], 10) {
            return format!("#{:#x}{}", (!num).wrapping_add(1), suffix);
        }
        if let Ok(num) = u64::from_str_radix(&num[1..], 10) {
            return format!("#{:#x}{}", (!num).wrapping_add(1), suffix);
        }
    } else {
        if let Ok(num) = num.parse::<u32>() {
            return format!("#{:#x}{}", num, suffix);
        }
        if let Ok(num) = num.parse::<u64>() {
            return format!("#{:#x}{}", num, suffix);
        }
    }

    s.to_string()
}

fn try_sve_shorthand(s: &str) -> String {
    if let Some(begin) = s.find('{') {
        if s.find('-').is_some() {
            return s.replace(" - ", "-").to_string();
        }
        let close = s.find('}').unwrap();
        let list = &s[begin..close];

        let parts = list.split(',');
        if parts.clone().count() < 2 {
            return s.to_string();
        }
        let first = parts.clone().next().unwrap().trim();
        let last = parts.clone().last().unwrap().trim();
        let shorthand = format!("{}-{}", first, last);
        return s.replace(list, &shorthand);
    }
    s.to_string()
}

fn normalize_moves(tokens: &[&str]) -> Option<String> {
    if tokens.len() < 5 {
        return None;
    }

    if tokens[0] != "movk" && tokens[0] != "movz" && tokens[0] != "movn" {
        return None;
    }

    let get_imm = |imm_str: &str| {
        if imm_str.starts_with("0x") {
            if let Ok(num) = u32::from_str_radix(&imm_str[2..], 16) {
                Some(num as u64)
            } else if let Ok(num) = u64::from_str_radix(&imm_str[2..], 16) {
                Some(num)
            } else {
                None
            }
        } else if let Ok(num) = imm_str.parse::<u32>() {
            Some(num as u64)
        } else if let Ok(num) = imm_str.parse::<u64>() {
            Some(num)
        } else {
            None
        }
    };

    let lsl = get_imm(&tokens[4][1..])?;
    let num = get_imm(&tokens[2][1..tokens[2].len() - 1])?;

    if tokens[0] == "movk" && tokens.len() == 5 && tokens[3] == "lsl" && lsl == 0 {
        return Some(format!(
            "{} {}",
            tokens[1],
            &tokens[2][..tokens[2].len() - 1]
        ));
    }

    if tokens[0] == "movz" && tokens.len() == 5 && tokens[3] == "lsl" {
        return Some(format!("{} #{:#x}", tokens[1], num << lsl));
    }

    if tokens[0] == "movn" && tokens.len() == 5 && tokens[3] == "lsl" {
        if tokens[1].starts_with('w') {
            return Some(format!("{} #{:#x}", tokens[1], !(num << lsl) as i32));
        }
        return Some(format!("{} #{:#x}", tokens[1], !(num << lsl)));
    }

    None
}

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <file>", args[0]);
        std::process::exit(1);
    }

    let file = File::open(&args[1])?;
    let reader = BufReader::new(file);

    for line in reader.lines() {
        let line = line?;
        let line = if let Some(pos) = line.find("//") {
            &line[..pos]
        } else {
            &line
        };

        let line = if let Some(pos) = line.find("<_binary") {
            &line[..pos]
        } else {
            line
        };

        let line = line.trim();
        let line = line.to_lowercase();
        let tokens: Vec<&str> = line.split_whitespace().collect();
        if line.contains("<unknown>") || line.contains("<undefined>") || line.contains(".inst") {
            let opcode = tokens[1];
            if u32::from_str_radix(opcode, 16).is_err() {
                continue;
            }
            println!("{:14}{:16}", opcode, "<unknown>");
            continue;
        }

        if tokens.len() <= 2 || !tokens[0].ends_with(':') {
            continue;
        }

        let opcode = tokens[1];
        if u32::from_str_radix(opcode, 16).is_err() {
            continue;
        }

        let mut mnemonic = tokens[2];

        let operands = if let Some(mov) = normalize_moves(&tokens[2..]) {
            if mnemonic == "movk" {
                mnemonic = "movk";
            } else {
                mnemonic = "mov";
            }
            mov
        } else {
            tokens[3..]
                .iter()
                .map(|&x| try_hex(x))
                .collect::<Vec<String>>()
                .join(" ")
                .replace("{ ", "{")
                .replace(" }", "}")
        };

        if mnemonic.starts_with("ld") && operands.contains(", wzr, ") {
            println!(
                "{:14}{:16}{}",
                opcode,
                mnemonic.replace("ld", "st"),
                operands.replace(", wzr, ", ", ")
            );
            continue;
        } else if mnemonic.starts_with("ld") && operands.contains(", xzr, ") {
            println!(
                "{:14}{:16}{}",
                opcode,
                mnemonic.replace("ld", "st"),
                operands.replace(", xzr, ", ", ")
            );
            continue;
        }

        if mnemonic.starts_with("sbc") && operands.contains(", wzr, ") {
            println!(
                "{:14}{:16}{}",
                opcode,
                mnemonic.replace("sbc", "ngc"),
                operands.replace(", wzr, ", ", ")
            );
            continue;
        } else if mnemonic.starts_with("sbc") && operands.contains(", xzr, ") {
            println!(
                "{:14}{:16}{}",
                opcode,
                mnemonic.replace("sbc", "ngc"),
                operands.replace(", xzr, ", ", ")
            );
            continue;
        } else if mnemonic == "sbfm" {
            let rd = &tokens[3][..tokens[3].len() - 1];
            let rn = &tokens[4][..tokens[4].len() - 1];
            let immr = &tokens[5][1..tokens[5].len() - 1];
            let imms = &tokens[6][1..];

            let immr = if let Ok(immr) = u64::from_str_radix(immr, 10) {
                Some(immr)
            } else if let Ok(immr) = u64::from_str_radix(&immr[2..], 16) {
                Some(immr)
            } else {
                None
            };
            let imms = if let Ok(imms) = u64::from_str_radix(imms, 10) {
                Some(imms)
            } else if let Ok(imms) = u64::from_str_radix(&imms[2..], 16) {
                Some(imms)
            } else {
                None
            };

            if immr.is_some() && imms.is_some() {
                /*
                   Aliases for `sbfm Rd, Rn, #immr, #imms``:

                   ASR (immediate)	32-bit	imms == '011111'
                   ASR (immediate)	64-bit	imms == '111111'
                   SBFIZ		UInt(imms) < UInt(immr)
                   SBFX		BFXPreferred(sf, opc<1>, imms, immr)
                   SXTB		immr == '000000' && imms == '0b000111'
                   SXTH		immr == '000000' && imms == '0b001111'
                   SXTW		immr == '000000' && imms == '0b011111'
                */

                let immr = immr.unwrap();
                let imms = imms.unwrap();
                if imms < immr {
                    let imms = imms + 1;
                    let immr = if rd.starts_with('w') {
                        0x20 - immr
                    } else {
                        0x40 - immr
                    };
                    println!(
                        "{opcode:14}{:16}{rd}, {rn}, #{immr:#x}, #{imms:#x}",
                        "sbfiz"
                    );
                    continue;
                } else if rd.starts_with('x') && imms == 0b111111
                    || rd.starts_with('w') && imms == 0b11111
                {
                    println!("{opcode:14}{:16}{rd}, {rn}, #{immr:#x}", "asr");
                    continue;
                } else if immr == 0 && imms == 0b111 {
                    println!("{opcode:14}{:16}{rd}, {}", "sxtb", rn.replace('x', "w"));
                    continue;
                } else if immr == 0 && imms == 0b1111 {
                    println!("{opcode:14}{:16}{rd}, {}", "sxth", rn.replace('x', "w"));
                    continue;
                } else if immr == 0 && imms == 0b11111 {
                    println!("{opcode:14}{:16}{rd}, {}", "sxtw", rn.replace('x', "w"));
                    continue;
                }
            }
        } else if mnemonic == "extr" {
            if tokens[4] == tokens[5] {
                println!(
                    "{:14}{:16}{}",
                    opcode,
                    "ror",
                    operands.replace(format!("{} {}", tokens[4], tokens[5]).as_str(), tokens[4])
                );
            }
            continue;
        }

        if mnemonic.starts_with("dcps") {
            println!("{:14}{:16}", opcode, mnemonic);
            continue;
        }

        if mnemonic == "ret" && operands == "x30" {
            println!("{:14}{:16}", opcode, mnemonic);
            continue;
        }

        let operands = try_sve_shorthand(&operands);
        println!("{:14}{:16}{}", opcode, mnemonic, operands);
    }

    Ok(())
}
