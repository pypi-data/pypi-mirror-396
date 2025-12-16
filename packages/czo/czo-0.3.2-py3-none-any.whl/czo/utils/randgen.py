import hashlib
import ipaddress
import random
import secrets
import shutil
import string
import uuid

from . import add_help


@add_help
class Rand:
    """
    随机生成一些测试数据
    """

    @staticmethod
    def help() -> None: ...

    @staticmethod
    def random_file(data: str | None = None) -> tuple:
        """
        生成随机文件并返回文件路径和文件的 MD5 哈希值。

        该函数用于生成一个随机文件，并返回该文件的路径和MD5哈希值。
        可以通过传入参数指定文件内容，默认为None。函数首先生成一个随机字符串作为
        临时文件的名称。然后，根据传入的内容将文件写入临时文件中。
        最后，使用hashlib库计算临时文件的MD5哈希值，并将临时文件移动到指定路径上。
        函数返回一个包含文件路径和MD5哈希值的元组。

        Args:
            data (str | None, optional): 文件内容，默认为 None。

        Returns:
            tuple: 包含文件路径和文件的 MD5 哈希值的元组。

        Example:
            ```python
            result = random_file(data='Hello, World!')
            print(result)  # 输出: ("./file", "a1b2c3d4e5f6...")
            ```
        """

        rand_str: list[str] = random.sample(string.ascii_letters + string.digits, 20)
        random_value: str = "".join(rand_str) + "\n" + str(uuid.uuid4())

        temp_name = f".{Rand.random_hash()}"
        with open(temp_name, "w") as w:
            if data is not None:
                w.write(f"{data}\n{random_value}")
            else:
                w.write(f"{random_value}")
        with open(temp_name, "rb") as r:
            md5: str = hashlib.md5(r.read()).hexdigest()
        temp_path: str = f"./{md5}"
        shutil.move(temp_name, temp_path)
        return temp_path, md5

    @staticmethod
    def random_int(length: int = 1) -> int:
        """生成随机数"""
        return int("".join(str(secrets.randbelow(10)) for _ in range(length)))

    @staticmethod
    def random_zh(length: int = 1) -> str:
        """生成随机中文"""
        chars: list[str] = []
        for _ in range(length):
            char: str = chr(random.randint(0x4E00, 0x9FA5))
            chars.append(char)
        return "".join(chars)

    @staticmethod
    def random_str(length: int = 1, mark: bool = False) -> str:
        """
        生成指定长度的随机大小写字母、数字组成的字符串。

        Args:
            length (int): 字符串长度。越短重复的概率越高。
            mark (bool, optional): 默认生成的字符串是否包含标点符号，默认为 False。
        """

        # 选择字符集
        characters = string.ascii_letters + string.digits

        if mark:
            characters += string.punctuation

        sys_random = random.SystemRandom()

        return "".join(sys_random.choice(characters) for _ in range(length))

    @staticmethod
    def random_hash(len: int | None = None) -> str:
        """
        生成一个随机的MD5哈希字符串。

        Args:
        - len: int | None - 生成的哈希字符串的长度。如果为None，则返回完整的MD5哈希字符串（32个字符）。

        Returns:
        - str: 生成的MD5哈希字符串。根据`len`参数可能被截断。
        """
        rand: str = "".join(random.sample(string.printable, 10))
        return hashlib.md5(rand.encode()).hexdigest()[:len]

    @staticmethod
    def random_hash_by_uuid4(len: int | None = None) -> str:
        """
        生成一个基于UUID4的随机哈希字符串。

        Args:
        - len: 需要返回的哈希字符串的长度。如果为None，则返回整个哈希字符串。

        Returns:
        - str: 根据指定长度生成的哈希字符串。
        """
        return hashlib.md5(uuid.uuid4().bytes).hexdigest()[:len]

    @staticmethod
    def random_ip(v6: bool = False) -> str:
        """
        生成一个随机的IP地址。

        Args:
        - v6: bool - 指定生成的IP地址版本。如果为True，则生成IPv6地址；否则生成IPv4地址。

        Returns:
        - str: 生成的IP地址。
        """
        if v6:
            return ipaddress.IPv6Address(random.randint(0, 2**128 - 1)).compressed
        else:
            return ipaddress.IPv4Address(random.randint(0, 2**32 - 1)).compressed

    @staticmethod
    def generate_ip_with_suffix(suffix: int = 0, *, v6: bool = False) -> str:
        """生成 IP 地址，并设置后缀"""
        if v6:
            return (
                ":".join([f"{random.randint(0, 65535):x}" for _ in range(4)])
                + f"::{suffix}"
            )
        else:
            return (
                ".".join([f"{random.randint(0, 255)}" for _ in range(3)]) + f".{suffix}"
            )

    @staticmethod
    def generate_ip_with_range(is_ipv6: bool = False):
        """
        生成一个IP地址范围，可以是IPv4或IPv6地址格式。

        Args:
        - is_ipv6: bool 值，用于指定生成IPv4还是IPv6地址范围。默认为False，表示生成IPv4地址范围。

        Returns:
        - 返回一个字符串，表示IP地址范围。如果is_ipv6为True，则返回IPv6地址范围，否则返回IPv4地址范围。
        """
        if is_ipv6:
            ip = ":".join([f"{random.randint(0, 65535):x}" for _ in range(4)])
            return f"{ip}::{random.randint(1, 10000):x}-{ip}::{random.randint(20000, 65500):x}"
        else:
            ip = ".".join([f"{random.randint(0, 255)}" for _ in range(3)])
            return f"{ip}.{random.randint(1, 100)}-{ip}.{random.randint(110, 254)}"

    @staticmethod
    def generate_ip_with_netmask(netmask: int | None = None, *, v6: bool = False):
        """
        生成一个随机的IP子网掩码格式。
        """
        if v6:
            netmask = netmask if netmask is not None else random.randint(64, 128)
            return f"{Rand.generate_ip_with_suffix(v6=v6)}/{netmask}"
        else:
            netmask = netmask if netmask is not None else random.randint(8, 32)
            return f"{Rand.generate_ip_with_suffix()}/{netmask}"

    @staticmethod
    def random_mac() -> str:
        """生成随机 MAC 地址"""
        return ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))

    @staticmethod
    def random_email(domain: str | None = None, *, length: int = 8) -> str:
        """生成随机邮箱"""
        domains = [
            "example.com",
            "test.local",
            "mail.test",
            "demo.dev",
            "sample.org",
        ]
        prefix = Rand.random_str(length).lower()
        selected_domain = domain if domain else random.choice(domains)
        return f"{prefix}@{selected_domain}"

    @staticmethod
    def random_url(domain: str | None = None, *, https: bool = True) -> str:
        """生成随机 URL，便于构造 HTTP 相关测试数据"""
        domains = ["example.com", "localhost", "demo.dev", "service.test"]
        chosen_domain = domain or random.choice(domains)
        scheme = "https" if https else "http"
        path = "/".join([Rand.random_str(6).lower(), Rand.random_str(8).lower()])
        return f"{scheme}://{chosen_domain}/{path}"
