"""
AI 验证系统的核心数据模型

定义了系统中使用的所有数据结构，包括市场数据、形态候选、
AI 响应、验证结果和配置信息等。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from enum import Enum


# 交易方向常量
BUY_SIDE = "buy"
SELL_SIDE = "sell"


class PatternType(Enum):
    """形态类型枚举"""

    EQUAL_HIGH = "equal_high"
    EQUAL_LOW = "equal_low"


class TradingDecision(Enum):
    """交易决策枚举"""

    EXECUTE = "execute"
    SKIP = "skip"
    FALLBACK = "fallback"


@dataclass
class Point:
    """价格点数据结构"""

    timestamp: datetime
    price: float
    volume: float = 0.0
    index: int = 0


@dataclass
class OHLCV:
    """OHLCV K线数据结构"""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class TechnicalIndicators:
    """技术指标数据结构"""

    rsi: Optional[List[float]] = None
    macd: Optional[Dict[str, List[float]]] = None
    ema: Optional[Dict[str, List[float]]] = None
    sma: Optional[Dict[str, List[float]]] = None
    bollinger_bands: Optional[Dict[str, List[float]]] = None
    atr: Optional[List[float]] = None
    volume_sma: Optional[List[float]] = None


@dataclass
class MarketData:
    """市场数据结构"""

    trading_pair: str
    candles: List[OHLCV]
    timestamp: datetime
    technical_indicators: Optional[TechnicalIndicators] = None

    def __post_init__(self):
        """数据验证"""
        if not self.candles:
            raise ValueError("K线数据不能为空")
        if len(self.candles) < 50:
            raise ValueError("K线数据至少需要50根")


@dataclass
class PatternCandidate:
    """形态候选结构"""

    pattern_type: PatternType
    points: List[Point]
    confidence: float
    timeframe: str
    start_time: datetime
    end_time: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """数据验证"""
        if not self.points:
            raise ValueError("形态点不能为空")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("置信度必须在0-1之间")


@dataclass
class AIInputData:
    """AI模型输入数据结构"""

    market_data: MarketData
    pattern_candidates: List[PatternCandidate]
    additional_features: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于API调用"""
        return {
            "trading_pair": self.market_data.trading_pair,
            "candles": [
                {
                    "timestamp": candle.timestamp.isoformat(),
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                    "volume": candle.volume,
                }
                for candle in self.market_data.candles
            ],
            "patterns": [
                {
                    "type": pattern.pattern_type.value,
                    "points": [
                        {
                            "timestamp": point.timestamp.isoformat(),
                            "price": point.price,
                            "volume": point.volume,
                            "index": point.index,
                        }
                        for point in pattern.points
                    ],
                    "confidence": pattern.confidence,
                    "timeframe": pattern.timeframe,
                    "start_time": pattern.start_time.isoformat(),
                    "end_time": pattern.end_time.isoformat(),
                    "metadata": pattern.metadata,
                }
                for pattern in self.pattern_candidates
            ],
            "technical_indicators": self._serialize_indicators(),
            "additional_features": self.additional_features,
        }

    def _serialize_indicators(self) -> Optional[Dict[str, Any]]:
        """序列化技术指标"""
        if not self.market_data.technical_indicators:
            return None

        indicators = self.market_data.technical_indicators
        return {
            "rsi": indicators.rsi,
            "macd": indicators.macd,
            "ema": indicators.ema,
            "sma": indicators.sma,
            "bollinger_bands": indicators.bollinger_bands,
            "atr": indicators.atr,
            "volume_sma": indicators.volume_sma,
        }


@dataclass
class AIValidationResponse:
    """AI验证响应结构"""

    confidence: float
    reasoning: str
    feature_importance: Dict[str, float]
    model_version: str
    processing_time: float
    side: str = ""  # 交易方向: "buy" 或 "sell"
    raw_response: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """数据验证"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("置信度必须在0-1之间")
        if self.processing_time < 0:
            raise ValueError("处理时间不能为负数")
        if self.side and self.side not in [BUY_SIDE, SELL_SIDE]:
            raise ValueError(f"交易方向必须是 '{BUY_SIDE}' 或 '{SELL_SIDE}'")


@dataclass
class ValidationResult:
    """验证结果结构"""

    success: bool
    confidence: float
    decision: TradingDecision
    ai_response: Optional[AIValidationResponse] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """数据验证"""
        if self.success and self.ai_response is None:
            raise ValueError("成功的验证结果必须包含AI响应")
        if not self.success and self.error_message is None:
            raise ValueError("失败的验证结果必须包含错误信息")


@dataclass
class AIValidationConfig:
    """AI验证配置"""

    enabled: bool = True
    confidence_threshold: float = 0.6
    timeout_seconds: int = 5
    max_retries: int = 3
    fallback_mode: str = "skip"  # 'skip' | 'execute'
    data_collection_candles: int = 200
    enable_caching: bool = True
    cache_ttl_seconds: int = 300

    def __post_init__(self):
        """配置验证"""
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("置信度阈值必须在0-1之间")
        if self.timeout_seconds <= 0:
            raise ValueError("超时时间必须大于0")
        if self.max_retries < 0:
            raise ValueError("重试次数不能为负数")
        if self.fallback_mode not in ["skip", "execute"]:
            raise ValueError("降级模式必须是 'skip' 或 'execute'")
        if self.data_collection_candles < 50:
            raise ValueError("数据收集K线数量至少需要50根")


@dataclass
class AIServiceConfig:
    """AI服务配置"""

    endpoint_url: str
    api_key: str
    model_version: str = "v1.0"
    timeout: int = 5
    max_retries: int = 3
    headers: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """配置验证"""
        if not self.endpoint_url:
            raise ValueError("AI服务端点URL不能为空")
        if not self.api_key:
            raise ValueError("API密钥不能为空")
        if self.timeout <= 0:
            raise ValueError("超时时间必须大于0")
        if self.max_retries < 0:
            raise ValueError("重试次数不能为负数")


@dataclass
class PerformanceMetrics:
    """性能指标数据结构"""

    total_validations: int = 0
    successful_validations: int = 0
    failed_validations: int = 0
    average_response_time: float = 0.0
    confidence_distribution: Dict[str, int] = field(default_factory=dict)
    error_counts: Dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_validations == 0:
            return 0.0
        return self.successful_validations / self.total_validations

    @property
    def failure_rate(self) -> float:
        """失败率"""
        return 1.0 - self.success_rate


@dataclass
class ValidationStats:
    """验证统计信息"""

    period_start: datetime
    period_end: datetime
    total_validations: int
    success_rate: float
    average_confidence: float
    confidence_distribution: Dict[str, int]
    decision_distribution: Dict[str, int]
    average_processing_time: float
    error_summary: Dict[str, int]
