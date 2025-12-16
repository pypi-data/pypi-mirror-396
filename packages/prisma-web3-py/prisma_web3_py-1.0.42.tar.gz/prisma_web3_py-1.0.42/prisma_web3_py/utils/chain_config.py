"""
Chain configuration and mapping utilities.

Provides standardized chain names, abbreviations, and priority ordering.
"""

from typing import Dict, List, Optional


class ChainConfig:
    """
    Chain configuration with CoinGecko standard names and abbreviations.

    Database stores CoinGecko standard names, application layer uses abbreviations.
    """

    # CoinGecko 标准名称 -> 缩写映射
    CHAIN_ABBREVIATIONS: Dict[str, str] = {
        "ethereum": "eth",
        "binance-smart-chain": "bsc",
        "solana": "sol",
        "base": "base",
        "arbitrum-one": "arb",
        "polygon-pos": "poly",
        "avalanche": "avax",
        "optimistic-ethereum": "op",
        "fantom": "ftm",
        "harmony-shard-0": "one",
        "near-protocol": "near",
        "zksync": "zksync",
        "mantle": "mnt",
        "linea": "linea",
        "osmosis": "osmo",
        "sui": "sui",
        "berachain": "bera",
        "unichain": "uni",
        "energi": "nrg",
        "hyperevm": "hype",
    }

    # 缩写 -> CoinGecko 标准名称映射（反向）
    ABBREVIATION_TO_CHAIN: Dict[str, str] = {
        v: k for k, v in CHAIN_ABBREVIATIONS.items()
    }

    # 主链优先级（数字越小优先级越高）
    CHAIN_PRIORITY: List[str] = [
        "ethereum",              # 1. ETH - 最高优先级
        "binance-smart-chain",   # 2. BSC
        "base",                  # 3. Base
        "arbitrum-one",          # 4. Arbitrum
        "optimistic-ethereum",   # 5. Optimism
        "polygon-pos",           # 6. Polygon
        "solana",                # 7. Solana
        "avalanche",             # 8. Avalanche
        "fantom",                # 9. Fantom
        "zksync",                # 10. zkSync
        "mantle",                # 11. Mantle
        "linea",                 # 12. Linea
        "near-protocol",         # 13. Near
        "harmony-shard-0",       # 14. Harmony
        "osmosis",               # 15. Osmosis
        "sui",                   # 16. Sui
        "berachain",             # 17. Berachain
        "unichain",              # 18. Unichain
    ]

    # 链的显示名称
    CHAIN_DISPLAY_NAMES: Dict[str, str] = {
        "ethereum": "Ethereum",
        "binance-smart-chain": "BNB Chain",
        "solana": "Solana",
        "base": "Base",
        "arbitrum-one": "Arbitrum",
        "polygon-pos": "Polygon",
        "avalanche": "Avalanche",
        "optimistic-ethereum": "Optimism",
        "fantom": "Fantom",
        "harmony-shard-0": "Harmony",
        "near-protocol": "NEAR",
        "zksync": "zkSync",
        "mantle": "Mantle",
        "linea": "Linea",
        "osmosis": "Osmosis",
        "sui": "Sui",
        "berachain": "Berachain",
        "unichain": "Unichain",
        "energi": "Energi",
        "hyperevm": "HyperEVM",
    }

    @classmethod
    def get_abbreviation(cls, chain: str) -> str:
        """
        获取链的缩写。

        Args:
            chain: CoinGecko 标准链名称

        Returns:
            链的缩写，如果未找到则返回原名称

        Example:
            >>> ChainConfig.get_abbreviation("ethereum")
            'eth'
            >>> ChainConfig.get_abbreviation("binance-smart-chain")
            'bsc'
        """
        return cls.CHAIN_ABBREVIATIONS.get(chain, chain)

    @classmethod
    def get_standard_name(cls, abbreviation: str) -> str:
        """
        从缩写获取 CoinGecko 标准链名称。

        Args:
            abbreviation: 链的缩写

        Returns:
            CoinGecko 标准链名称，如果未找到则返回原输入

        Example:
            >>> ChainConfig.get_standard_name("eth")
            'ethereum'
            >>> ChainConfig.get_standard_name("bsc")
            'binance-smart-chain'
        """
        # 如果已经是标准名称，直接返回
        if abbreviation in cls.CHAIN_ABBREVIATIONS:
            return abbreviation
        # 否则从缩写映射中查找
        return cls.ABBREVIATION_TO_CHAIN.get(abbreviation.lower(), abbreviation)

    @classmethod
    def get_display_name(cls, chain: str) -> str:
        """
        获取链的显示名称。

        Args:
            chain: CoinGecko 标准链名称或缩写

        Returns:
            链的显示名称

        Example:
            >>> ChainConfig.get_display_name("ethereum")
            'Ethereum'
            >>> ChainConfig.get_display_name("eth")
            'Ethereum'
        """
        standard_name = cls.get_standard_name(chain)
        return cls.CHAIN_DISPLAY_NAMES.get(standard_name, standard_name.title())

    @classmethod
    def get_priority(cls, chain: str) -> int:
        """
        获取链的优先级（数字越小优先级越高）。

        Args:
            chain: CoinGecko 标准链名称或缩写

        Returns:
            优先级数字，未在列表中的链返回 999

        Example:
            >>> ChainConfig.get_priority("ethereum")
            0
            >>> ChainConfig.get_priority("eth")
            0
        """
        standard_name = cls.get_standard_name(chain)
        try:
            return cls.CHAIN_PRIORITY.index(standard_name)
        except ValueError:
            return 999  # 未在优先级列表中的链

    @classmethod
    def is_valid_chain(cls, chain: str) -> bool:
        """
        检查是否是有效的链名称或缩写。

        Args:
            chain: 链名称或缩写

        Returns:
            True 如果是有效的链
        """
        return (chain in cls.CHAIN_ABBREVIATIONS or
                chain.lower() in cls.ABBREVIATION_TO_CHAIN)

    @classmethod
    def get_all_chains(cls, use_abbreviations: bool = False) -> List[str]:
        """
        获取所有支持的链列表（按优先级排序）。

        Args:
            use_abbreviations: True 返回缩写，False 返回标准名称

        Returns:
            链列表
        """
        if use_abbreviations:
            return [cls.get_abbreviation(chain) for chain in cls.CHAIN_PRIORITY]
        return cls.CHAIN_PRIORITY.copy()

    @classmethod
    def normalize_chain(cls, chain: str) -> str:
        """
        标准化链名称（转换为 CoinGecko 标准格式）。

        这个方法用于数据库操作，确保存储的是标准名称。

        Args:
            chain: 链名称或缩写

        Returns:
            CoinGecko 标准链名称

        Example:
            >>> ChainConfig.normalize_chain("eth")
            'ethereum'
            >>> ChainConfig.normalize_chain("ethereum")
            'ethereum'
        """
        return cls.get_standard_name(chain)


# 常用的链缩写（方便快速访问）
class Chain:
    """常用链的缩写常量。"""
    ETH = "eth"
    BSC = "bsc"
    SOL = "sol"
    BASE = "base"
    ARB = "arb"
    POLY = "poly"
    AVAX = "avax"
    OP = "op"
    FTM = "ftm"
    NEAR = "near"

    # 标准名称
    ETHEREUM = "ethereum"
    BINANCE_SMART_CHAIN = "binance-smart-chain"
    SOLANA = "solana"
    ARBITRUM_ONE = "arbitrum-one"
    POLYGON_POS = "polygon-pos"
    AVALANCHE = "avalanche"
    OPTIMISTIC_ETHEREUM = "optimistic-ethereum"


# 便捷函数
def abbr(chain: str) -> str:
    """获取链的缩写。"""
    return ChainConfig.get_abbreviation(chain)


def standard(chain: str) -> str:
    """获取链的标准名称。"""
    return ChainConfig.get_standard_name(chain)


def display(chain: str) -> str:
    """获取链的显示名称。"""
    return ChainConfig.get_display_name(chain)


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("Chain Configuration Examples")
    print("=" * 60)

    # 示例1: 缩写转换
    print("\n1. 缩写转换:")
    print(f"  ethereum -> {abbr('ethereum')}")
    print(f"  binance-smart-chain -> {abbr('binance-smart-chain')}")
    print(f"  eth -> {standard('eth')}")
    print(f"  bsc -> {standard('bsc')}")

    # 示例2: 显示名称
    print("\n2. 显示名称:")
    print(f"  ethereum -> {display('ethereum')}")
    print(f"  eth -> {display('eth')}")
    print(f"  bsc -> {display('bsc')}")

    # 示例3: 优先级
    print("\n3. 链优先级:")
    chains = ["ethereum", "solana", "polygon-pos", "arbitrum-one"]
    sorted_chains = sorted(chains, key=ChainConfig.get_priority)
    for i, chain in enumerate(sorted_chains, 1):
        priority = ChainConfig.get_priority(chain)
        print(f"  {i}. {display(chain):15} (priority: {priority})")

    # 示例4: 所有支持的链
    print("\n4. 所有支持的链（Top 10）:")
    all_chains = ChainConfig.get_all_chains()[:10]
    for i, chain in enumerate(all_chains, 1):
        abbr_name = abbr(chain)
        disp_name = display(chain)
        print(f"  {i:2}. {chain:25} -> {abbr_name:6} ({disp_name})")

    print("\n" + "=" * 60)
