import hashlib

try:
    from Crypto.Hash import MD5, keccak
    HAS_PYCRYPTODOME = True
except ModuleNotFoundError:
    HAS_PYCRYPTODOME = False


def calc_md5(data: str) -> str:
    if HAS_PYCRYPTODOME:
        return MD5.new(data=data.encode()).hexdigest()
    return hashlib.md5(data.encode()).hexdigest()


def calc_keccak384(data: str) -> str:
    if HAS_PYCRYPTODOME:
        return keccak.new(data=data.encode(), digest_bits=384).hexdigest()

    # hashlib does not provide keccak, this fallback keeps script executable.
    return hashlib.sha3_384(data.encode()).hexdigest()


def show_activation_codes_legacy(machine_id: str) -> None:
    print("FinalShell < 3.9.6")
    print("Advanced:", calc_md5(f"61305{machine_id}8552")[8:24])
    print("Professional:", calc_md5(f"2356{machine_id}13593")[8:24])


def show_activation_codes_modern(machine_id: str) -> None:
    print("FinalShell >= 3.9.6")
    print("Advanced:", calc_keccak384(f"{machine_id}hSf(78cvVlS5E")[12:28])
    print("Professional:", calc_keccak384(f"{machine_id}FF3Go(*Xvbb5s2")[12:28])

    print("FinalShell 4.5")
    print("Advanced:", calc_keccak384(f"{machine_id}wcegS3gzA$")[12:28])
    print("Professional:", calc_keccak384(f"{machine_id}b(xxkHn%z);x")[12:28])

    print("FinalShell 4.6")
    print("Advanced:", calc_keccak384(f"{machine_id}csSf5*xlkgYSX,y")[12:28])
    print("Professional:", calc_keccak384(f"{machine_id}Scfg*ZkvJZc,s,Y")[12:28])


def main() -> None:
    machine_id = input("请输入机器码:").strip()
    if not machine_id:
        print("机器码不能为空")
        return

    if not HAS_PYCRYPTODOME:
        print("Warning: pycryptodome not found; using hashlib.sha3_384 fallback.")

    show_activation_codes_legacy(machine_id)
    show_activation_codes_modern(machine_id)


if __name__ == "__main__":
    main()
