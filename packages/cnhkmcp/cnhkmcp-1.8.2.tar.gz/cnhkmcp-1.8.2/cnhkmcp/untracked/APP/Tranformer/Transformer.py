import requests
import json
import sys
import asyncio
import openai
import re
from typing import Optional, Union # Added this import
import logging
import pandas as pd
import os
from pathlib import Path
from urllib.parse import urljoin
import time
import threading
import itertools
import getpass
import io
import validator as val
from ace_lib import get_instrument_type_region_delay
# Force stdout/stderr to use utf-8 on Windows to avoid UnicodeEncodeError
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except Exception:
        pass

# 这些变量将在交互式输入中设置
LLM_model_name = None
LLM_API_KEY = None
llm_base_url = None
username = None
password = None
DATA_CATEGORIES = None


template_summary = """# BRAIN论坛Alpha模板精华总结

本文档旨在系统性地整理和总结优秀Alpha模板。所有内容均源自社区顾问的无私分享或公开文件，并经过了初步的筛选和整合。每个模板都附有其核心思想、变量说明、适用场景及原帖链接，方便您理解、应用和进一步探索。
使用时请思考如何将下列模板与有的Alpha表达式结合，创造出新的模板来捕捉和发现市场规律，找到”好“公司和”坏“公司
**使用前请注意：**
*   **过拟合风险**：部分模板可能存在过拟合风险，请谨慎使用，并结合IS-Ladder测试、多市场回测等方法进行验证。
*   **参数调整**：模板中的参数（如时间窗口、数据集字段）需要根据您的具体研究目标和数据特性进行调整。
*   **持续学习**：最好的模板是您自己创造的。希望本文档能激发您的灵感，而不是限制您的思维。

---

## From: Alpha Examples from Learn101

### Momentum after news
**Hypothesis**: After news is released, if a stock takes a longer time to rise, it may show strong evidence of upward momentum, and it could be beneficial to take a long position in it.
**Expression**: `ts_backfill(vec_avg(nws12_prez_4l),504)`
**Settings**: Region: USA, Universe: TOP500, Delay: 1, Decay: 0, Neutralization: INDUSTRY, Truncation: 0.08, Pasteurization: ON
**逻辑链深度解析**:
*   **时序相对性 (Step 4)**: 这是一个典型的时序信号。`ts_backfill` 的使用暗示了新闻数据是稀疏的（Step 4.2.4），需要填补空白以维持信号连续性。
*   **算子深意**: `vec_avg` 用于聚合多维新闻向量，提取核心情绪/强度；`ts_backfill` 确保在无新闻日也能维持上一次的观点，直到新消息到来。
**优化方向**:
*   **去噪 (Step 0)**: 新闻情绪可能存在极端噪音，建议在 `vec_avg` 后增加 `winsorize` 或 `rank`。
*   **从属信号 (Subordinate)**: 叠加 `Social Media Effect`。若新闻情绪好但社媒热度低（噪音少），则放大权重；若社媒过热，可能反转。
*   **门限交易 (Step 5)**: 仅在新闻情绪显著偏离均值时交易，如 `trade_when(abs(zscore(news)) > 1.5, ...)`。

### Pretax Income
**Hypothesis**: Pretax income is a good measure of a company's financial health and profitability.
**Expression**: `quantile(ts_rank(pretax_income,250))`
**Settings**: Region: USA, Universe: TOP3000, Delay: 1, Decay: 4, Neutralization: MARKET, Truncation: 0.01, Pasteurization: ON
**逻辑链深度解析**:
*   **时序相对性 (Step 4)**: `ts_rank(..., 250)` 比较当前收入与过去一年的水平，寻找“自身改善”而非“绝对高收入”。
*   **分布重塑 (Step 0)**: `quantile` 强制将信号拉伸为均匀分布，避免了极值影响，只关注相对排序。
**优化方向**:
*   **区间优化 (Step 2)**: 收入微弱变化可能只是噪音。可改用 `ts_zscore` 并只在 >1 或 <-1 时交易。
*   **从属信号**: 引入 `market_cap`。大市值的收入创新高可能比小市值更稳健（质量溢价）。

### Operating Earnings Yield
**Hypothesis**: If the operating income of a company is currently higher than its past 1 year history, buy the company's stock and vice-versa.
**Expression**: `ts_rank(operating_income,252)`
**Settings**: Region: USA, Universe: TOP3000, Delay: 1, Decay: 0, Neutralization: SUBINDUSTRY, Truncation: 0.08, Pasteurization: ON
**逻辑链深度解析**:
*   **时序相对性 (Step 4)**: 纯粹的时序动量逻辑。`ts_rank` 将当前值映射到历史分位，捕捉“业绩改善”趋势。
**优化方向**:
*   **组内比较 (Step 3)**: 考虑行业周期性。先做 `group_zscore(operating_income, industry)` 再做 `ts_rank`，剔除行业景气度影响，只看个股相对行业的改善。
*   **门限 (Step 5)**: `trade_when(ts_rank > 0.8, ...)` 只做多业绩显著改善的股票。

### Appreciation of liabilities
**Hypothesis**: An increase in the fair value of liabilities could indicate a higher cost than expected.
**Expression**: `-ts_rank(fn_liab_fair_val_l1_a,252)`
**Settings**: Region: USA, Universe: TOP3000, Delay: 1, Decay: 0, Neutralization: SUBINDUSTRY, Truncation: 0.08, Pasteurization: ON
**逻辑链深度解析**:
*   **反向信号**: 负号 `-` 表示这是一个反向指标（负债增加是坏事）。
*   **时序相对性**: 同样基于 `ts_rank`，关注负债相对于自身历史的增长速度。
**优化方向**:
*   **去噪**: 负债数据可能存在跳变，建议先 `winsorize`。
*   **从属信号**: 结合 `cash_flow`。若负债增加但现金流同时也大幅增加（良性杠杆），则不应做空。

### Deferred Revenue
**Hypothesis**: Firms with high deferred revenue will surprise the market in the future when the deferred revenue is recognized.
**Expression**: `ts_backfill(fnd6_drc, 252)/assets`
**Settings**: Region: USA, Universe: TOP3000, Delay: 1, Decay: 0, Neutralization: SECTOR, Truncation: 1, Pasteurization: ON
**逻辑链深度解析**:
*   **截面比较 (Step 3)**: 除以 `assets` 是为了标准化（Size Adjustment），使其在截面上可比。
*   **数据填补 (Step 0)**: `ts_backfill` 处理财报数据的低频更新特性。
**优化方向**:
*   **行业中性 (Step 3)**: 递延收入在软件/服务业常见，在制造业少见。必须做 `group_zscore(..., sector)` 或 `neutralize`，否则只是在做多特定行业。
*   **时序变化 (Step 4)**: 关注递延收入的 *增长率* `ts_delta`，而不仅仅是绝对值。

### Reducing debt
**Hypothesis**: Take a long position in companies whose debt has decreased compared to the past.
**Expression**: `-ts_quantile(debt, 126)`
**Settings**: Region: USA, Universe: TOP3000, Delay: 1, Decay: 0, Neutralization: MARKET, Truncation: 0.01, Pasteurization: ON
**逻辑链深度解析**:
*   **时序相对性**: `ts_quantile` 与 `ts_rank` 类似，捕捉债务下降趋势。
**优化方向**:
*   **从属信号**: 结合 `interest_coverage` (利息保障倍数)。只有在偿债能力弱的公司中，债务减少才最重要（困境反转逻辑）。

### Power of leverage
**Hypothesis**: Companies with high liability-to-asset ratios often leverage debt as a strategic tool.
**Expression**: `liabilities/assets`
**Settings**: Region: USA, Universe: TOP3000, Delay: 1, Decay: 0, Neutralization: MARKET, Truncation: 0.01, Pasteurization: ON
**逻辑链深度解析**:
*   **截面比较 (Step 3)**: 这是一个经典的截面因子（杠杆率）。
**优化方向**:
*   **非线性 (Step 1)**: 杠杆通常是倒U型关系（适度杠杆好，过高杠杆坏）。考虑使用 `bucket` 分段，或 `trade_when` 剔除极端高杠杆。
*   **行业中性**: 银行/地产杠杆天生高，必须行业中性化。

## From: Alpha Examples from Learn102

### Social Media Effect
**Hypothesis**: Poorly performing stocks are discussed more in general on social media platforms.
**Expression**: `-scl12_buzz`
**Settings**: Region: USA, Universe: TOP3000, Delay: 1, Decay: 0, Neutralization: INDUSTRY, Truncation: 0.01, Pasteurization: ON
**逻辑链深度解析**:
*   **反向指标**: 负号暗示“关注度高=坏事”（可能是负面新闻缠身）。
*   **原始信号**: 直接使用 `buzz`，假设线性关系。
**优化方向**:
*   **去噪 (Step 0)**: 社媒数据极值多，必须 `log` 或 `winsorize`。
*   **从属信号**: 结合 `sentiment`。若关注度高且情感为正，可能是好事；关注度高且情感负，才是做空机会。
*   **门限**: `trade_when(rank(buzz) > 0.9, ...)` 只在极度热门时做空。

### Valuation Disconnect Swing Short
**Hypothesis**: A stock with high momentum and value score correlation suggests a disconnect between the stock's price and its intrinsic value.
**Expression**: `-ts_corr(ts_backfill(fscore_momentum,66),ts_backfill(fscore_value,66),756)`
**Settings**: Region: USA, Universe: TOP200, Delay: 1, Decay: 0, Neutralization: INDUSTRY, Truncation: 0.08, Pasteurization: ON
**逻辑链深度解析**:
*   **高阶统计量**: 使用 `ts_corr` 捕捉两个因子之间的动态关系，而非因子本身。
*   **逻辑**: 动量与价值相关性高，意味着价格脱离基本面（泡沫），因此做空（负号）。
**优化方向**:
*   **窗口调整**: 756天（3年）非常长，捕捉的是长期结构变化。可尝试短窗口（如126天）捕捉短期背离。

### Network Dependence
**Hypothesis**: Long stocks of companies whose hub score of customers are low over the past two years.
**Expression**: `-ts_mean(pv13_ustomergraphrank_hub_rank,504)`
**Settings**: Region: USA, Universe: TOP1000, Delay: 1, Decay: 0, Neutralization: INDUSTRY, Truncation: 0.08, Pasteurization: ON
**逻辑链深度解析**:
*   **供应链逻辑**: 客户集中度/中心度过高可能意味着风险（依赖大客户）。
*   **平滑 (Step 4)**: `ts_mean(..., 504)` 说明这是一个非常慢的变量，关注长期结构。
**优化方向**:
*   **从属信号**: 结合 `volatility`。高依赖度+高波动 = 极度危险。

## From: Alpha Examples from Learn103

### News-driven Volatility
**Hypothesis**: Stocks of companies that face high differences in their prices after any news release can be subject to varying sentiments.
**Expression**: `(ts_arg_max(ts_backfill(news_session_range, 20), 60))`
**Settings**: Region: USA, Universe: TOP3000, Delay: 1, Decay: 0, Neutralization: SECTOR, Truncation: 0.08, Pasteurization: ON
**逻辑链深度解析**:
*   **事件驱动 (Step 4.2.3)**: `ts_arg_max` 寻找过去60天内波动最大的那一天（新闻日）。
*   **算子深意**: 这不是直接用波动率，而是用“最大波动发生的时间距离”作为信号。
**优化方向**:
*   **衰减逻辑**: 结合 `days_from_last_change` 或 `exp_decay`，让信号随时间减弱。
*   **从属信号**: 叠加 `IV Skew`。若波动大且 Skew 偏空，做空；若 Skew 偏多，做多。

### Implied Volatility Spread as a predictor
**Hypothesis**: If the Call Open interest is higher than the Put Open interest, the stock may rise based on the intensity of the implied volatility spread.
**Expression**: `trade_when(pcr_oi_270 < 1, (implied_volatility_call_270-implied_volatility_put_270), -1)`
**Settings**: Region: USA, Universe: TOP3000, Delay: 1, Decay: 4, Neutralization: MARKET, Truncation: 0.08, Pasteurization: ON
**逻辑链深度解析**:
*   **门限交易 (Step 5)**: `trade_when(pcr_oi < 1, ...)` 是典型的门禁逻辑。只有在看涨持仓量大于看跌时（情绪偏多），才使用 IV Spread 信号。
*   **条件分支**: 不满足条件时给 `-1`（做空），这是一个激进的二元策略。
**优化方向**:
*   **平滑**: IV 数据跳动大，建议对 Spread 做 `ts_mean` 或 `ts_decay_linear`。

## 《151 Trading Strategies》论文精华模板

本部分总结自Zura Kakushadze与Juan Andrés Serur合著的《151 Trading Strategies》一文，重点提炼其中适用于BRAIN平台的股票类策略，并将其泛化为可复用的Alpha模板。

---

### 1. 风险调整后动量模板 (Risk-Adjusted Momentum)

*   **模板表达式**: `ts_mean(ts_delay(returns, <skip_period>), <lookback_period>) / ts_std_dev(ts_delay(returns, <skip_period>), <lookback_period>)`
*   **核心思想**: 这是对经典动量因子的改进。它计算的是过去一段时间（lookback_period）的"时序夏普比率"，即收益均值除以收益波动。同时，`ts_delay`跳过了最近一段时间（skip_period，通常为21天/1个月）的数据，以规避短期反转效应的干扰。该因子旨在寻找那些"高质量"的、持续且平稳的动量。
*   **变量说明**:
    *   `<skip_period>`: 跳过的近期交易日数，如 `21`。
    *   `<lookback_period>`: 计算动量的回看窗口，如 `252`。
*   **适用场景**: 通用性强，适用于构建稳健的动量类Alpha。
*   **逻辑链深度解析**:
    *   **时序标准化 (Step 4)**: 分子是收益均值，分母是波动率。本质是 Rolling Sharpe Ratio。
    *   **去噪 (Step 0)**: `ts_delay` 跳过最近一个月，剔除了短期反转（Short-term Reversal）噪音，只保留中长期动量。
*   **优化方向**:
    *   **从属信号**: 叠加 `turnover`。在低换手率时，动量更可靠（量价配合）。
    *   **残差化**: 先对 returns 做 `regression_neut` 剔除大盘影响，计算纯特异性动量。
*   **适配自**: Section 3.1, "Price-momentum", `Rrisk.adj`

### 2. 标准化盈利超预期模板 (SUE - Standardized Unexpected Earnings)

*   **模板表达式**: `(fnd_eps_q - ts_delay(fnd_eps_q, 4)) / ts_std_dev(fnd_eps_q - ts_delay(fnd_eps_q, 4), 8)`
*   **核心思想**: 捕捉超预期的盈利增长。它计算的是最新一季的EPS相较于去年同期的增量，并用该增量自身过去8个季度的波动性进行标准化。标准化后的值（SUE）越高，代表盈利惊喜越大，是经典的盈利动量因子。
*   **变量说明**:
    *   `fnd_eps_q`: 季度每股收益（EPS）字段。
*   **适用场景**: `Fundamental`（基本面）数据集，用于事件驱动型Alpha。
*   **逻辑链深度解析**:
    *   **季节性调整**: `ts_delay(..., 4)` 比较同比季度，消除季节性影响。
    *   **波动率标准化 (Step 0)**: 除以过去8季度的波动，将“惊喜”转化为标准差单位（Z-Score），使其在不同波动率的公司间可比。
*   **优化方向**:
    *   **事件衰减 (Step 4)**: 叠加 `days_from_last_change`，让 SUE 信号随财报发布时间衰减。
    *   **从属信号**: 叠加 `Analyst Revision`。若 SUE 高且分析师上调预期，信号更强。
*   **适配自**: Section 3.2, "Earnings-momentum", SUE


### 4. 隐含波动率偏斜动量模板 (Implied Volatility Skew Momentum)

*   **模板表达式**: `ts_delta(implied_volatility_call_<window>, <period>) - ts_delta(implied_volatility_put_<window>, <period>)`
*   **核心思想**: 捕捉市场情绪的变化。看涨期权IV的上升通常与乐观情绪相关，而看跌期权IV的上升则与悲观或避险情绪相关。该模板计算Call IV的变化量与Put IV变化量之差，旨在做多情绪改善、做空情绪恶化的股票。
*   **变量说明**:
    *   `implied_volatility_call_<window>`: 不同期限的看涨期权隐含波动率。
    *   `implied_volatility_put_<window>`: 不同期限的看跌期权隐含波动率。
    *   `<period>`: 计算IV变化的时间窗口，如 `21` (月度变化)。
*   **适用场景**: `Option`（期权）数据集，用于捕捉短中期市场情绪变化。
*   **逻辑链深度解析**:
    *   **时序变化 (Step 4)**: 关注的是 IV 的 *变化* (`ts_delta`) 而非绝对值。
    *   **情绪差**: Call IV 涨幅 > Put IV 涨幅 -> 情绪改善。
*   **优化方向**:
    *   **门限**: `trade_when(abs(skew_delta) > threshold, ...)` 只在情绪剧烈变化时交易。
    *   **事件驱动**: 在财报前（IV 高企时）该策略可能失效，需用 `days_to_earnings` 过滤。
*   **适配自**: Section 3.5, "Implied volatility"

### 5. 残差动量模板 (Residual Momentum)

*   **模板表达式**: `ts_mean(regression_neut(regression_neut(regression_neut(returns, <factor_1/>), <factor_2/>), <factor_3/>), <window/>)`
*   **核心思想**: 提纯动量信号。传统动量可能包含了市场Beta、市值、价值等多种因子的敞口。此模板通过连续的中性化（例如依次对`<factor_1/>`, `<factor_2/>`, `<factor_3/>`执行`regression_neut`）剥离可被通用因子解释的部分，然后仅对无法被解释的"残差等价物"部分计算动量。
*   **变量说明**:
    *   `<factor_1/>`, `<factor_2/>`, `<factor_3/>`: 市场通用因子，如 `mkt_beta`, `size_factor`, `value_factor`。
    *   `<window/>`: 计算残差动量的时间窗口。
*   **适用场景**: 通用性强，是因子提纯、构建高质量Alpha的关键步骤。
*   **逻辑链深度解析**:
    *   **提纯 (Step 0)**: 通过连续 `regression_neut` 剥离 Beta、Size、Value 等风格暴露。
    *   **时序动量**: 对剥离后的残差求 `ts_mean`。
*   **优化方向**:
    *   **加权**: 使用 `ts_decay_linear` 代替 `ts_mean`，给予近期残差更大权重。
    *   **组内比较**: 在残差基础上再做 `group_rank`，寻找行业内最强特异动量。
*   **适配自**: Section 3.7, "Residual momentum"

### 6. 风险加权回归均值回归模板 (Weighted Regression Mean-Reversion)

*   **模板表达式**: `reverse(regression_neut(multiply(returns, power(inverse(ts_std_dev(returns, <window/>)), 2)), <group_matrix/>))`
*   **核心思想**: 这是对标准行业中性化均值回归的增强。在对收益率进行行业中性化时，它为不同股票赋予了不同的权重。具体来说，它给历史波动率较低的股票更高的权重，认为这些股票的收益率数据更"可靠"，在计算行业均值时应占更大比重。
*   **变量说明**:
    *   `<group_matrix>`: 行业或分组的哑变量矩阵。
    *   `weights`: 回归权重，通常是可靠性的度量，如 `1/variance`。
    *   `<window>`: 计算波动率的时间窗口。
*   **适用场景**: 适用于任何需要进行组内中性化或回归剥离的场景，尤其是当组内成员的信号质量或波动性差异较大时。
*   **逻辑链深度解析**:
    *   **加权最小二乘 (WLS)**: 使用 `1/variance` 作为权重，认为低波动的股票信息更可靠。
    *   **均值回归**: `reverse` 捕捉残差的反转。
*   **优化方向**:
    *   **从属信号**: 引入 `liquidity` 权重。流动性好的股票回归更快。
*   **适配自**: Section 3.10, "Mean-reversion – weighted regression"

### 7. 移动平均线交叉模板 (Moving Average Crossover)

*   **模板表达式**: `sign(ts_mean(<price/>, <short_window>) - ts_mean(<price/>, <long_window>))`
*   **核心思想**: 经典的趋势跟踪策略。当短期均线上穿长期均线（"金叉"）时，表明短期趋势走强，产生买入信号。当短期均线下穿长期均线（"死叉"）时，表明趋势走弱，产生卖出信号。
*   **变量说明**:
    *   `<price/>`: `close`, `vwap` 等价格字段。
    *   `<short_window>`: 短期均线窗口，如 `10`, `20`。
    *   `<long_window>`: 长期均线窗口，如 `50`, `100`。
*   **适用场景**: 适用于趋势性较强的市场或资产。
*   **逻辑链深度解析**:
    *   **低通滤波**: MA 本质是滤除高频噪音。
    *   **二元信号**: `sign` 输出 +1/-1，不包含强度信息。
*   **优化方向**:
    *   **连续化 (Step 1)**: 去掉 `sign`，直接使用差值并标准化 (`zscore`)，保留强度信息。
    *   **从属信号**: 结合 `ADX` (趋势强度指标)。只有在趋势强时才使用 MA 交叉。
*   **适配自**: Section 3.12, "Two moving averages"



### 9. 渠道突破模板 (Channel Breakout)

*   **模板表达式**: `alpha = if_else(greater(close, ts_max(high, <window/>)), 1, if_else(less(close, ts_min(low, <window/>)), -1, 0)); reverse(alpha)`
*   **核心思想**: 这是一个经典的反转策略。它定义了一个由过去N日最高价和最低价构成的价格渠道（Channel）。当价格向上突破渠道上轨时，认为市场过热，产生卖出信号（-1）；当价格向下突破渠道下轨时，认为市场超卖，产生买入信号（+1）。
*   **变量说明**:
    *   `<window>`: 定义渠道的时间窗口，如 `20`。
*   **适用场景**: 适用于有均值回归特性的市场或个股。
*   **逻辑链深度解析**:
    *   **区间突破 (Step 2)**: 典型的“只在尾部交易”逻辑。中间区间为 0。
    *   **反转逻辑**: `reverse` 赌突破是假突破（False Breakout）。
*   **优化方向**:
    *   **顺势/逆势切换**: 结合 `volatility`。低波时做反转（假突破），高波时做顺势（真突破）。
*   **适配自**: Section 3.15, "Channel"


### 11. 价值因子基础模板 (Value Factor)

*   **模板表达式**: `group_rank(<book_value/> / <market_cap/>)`
*   **核心思想**: 经典的价值投资策略。它旨在买入账面价值相对于市场价值被低估的"价值股"，并卖出被高估的"成长股"。最核心的衡量指标是账面市值比（Book-to-Price / Book-to-Market Ratio）。
*   **变量说明**:
    *   `<book_value/>`: 公司账面价值或每股净资产字段。
    *   `<market_cap/>`: 公司市值或收盘价字段。
*   **适用场景**: `Fundamental` (基本面) 数据集，作为构建多因子模型的基础因子之一。
*   **逻辑链深度解析**:
    *   **组内比较 (Step 3)**: 价值因子在不同行业间不可比（如科技 vs 银行），必须用 `group_rank`。
*   **优化方向**:
    *   **去噪**: 先 `winsorize` 再 `group_rank`。
    *   **从属信号**: 叠加 `Quality` (ROE)。避免买入“价值陷阱”（便宜但烂的公司）。
*   **适配自**: Section 3.3, "Value"



### 13. 配对交易均值回归框架 (Pairs Trading)

*   **模板表达式**: `signal_A = (close_A - close_B) - ts_mean(close_A - close_B, <window>); reverse(signal_A)`
*   **核心思想**: 寻找历史上高度相关的两只股票（一个"配对"），当它们的价差（spread）偏离历史均值时进行套利。如果价差过大，则做空价高的股票、做多价低的股票，赌价差会回归。这是一个经典的统计套利和均值回归策略。
*   **变量说明**:
    *   `close_A`, `close_B`: 配对股票A和B的价格序列。
    *   `<window>`: 计算历史价差均值的时间窗口。
*   **适用场景**: 适用于同一行业内业务高度相似的公司，是构建市场中性策略的基础。
*   **逻辑链深度解析**:
    *   **协整关系**: 构造平稳序列 `Spread`。
    *   **均值回归**: 赌 Spread 回归均值。
*   **优化方向**:
    *   **动态阈值**: 使用 `ts_std_dev(Spread)` 设定动态开仓线（如 2倍标准差）。
    *   **止损**: 增加 `trade_when(abs(Spread) > 4*std, 0, ...)` 防止协整破裂。
*   **适配自**: Section 3.8, "Pairs trading"

---

## 补充模板

### A. Analyst交叉分组打底（模板名：示例）
*   **核心结构**: `financial_data = ts_backfill(<vec_func/>(<analyst_metric/>), 60); gp = group_cartesian_product(country, industry); <ts_operator/>(<group_operator/>(financial_data, gp), <window/>)`
*   **思想**: 先对分析师字段做向量聚合（`vec_avg`、`vec_kurtosis`、`vec_ir`等），用`group_cartesian_product`构建国家×行业组合，再做组内标准化/中性化+时序处理，形成稳定的截面信号。
*   **变量要点**: `analyst_metric`覆盖`mdl26_*`、`star_arm_*`等Analyst/SmartEstimate场景；`vec_func`选择聚合方式；`group_operator`用于行业/国家组内的scale或neutralize；`ts_operator`用于时间平滑（`ts_mean`、`ts_zscore`等）；`window`在20/60/90/200之间取值。
*   **适用场景**: 适合Analyst情感、预期修正类主题，想要跨国+行业分组的稳健截面信号。
*   **逻辑链深度解析**:
    *   **数据填补 (Step 0)**: 分析师数据稀疏，必须 `ts_backfill`。
    *   **精细分组 (Step 3)**: `group_cartesian_product` 实现了“国家x行业”的精细化中性化，适合全球策略。
*   **优化方向**:
    *   **算子选择**: `vec_ir` (信息比率) 比 `vec_avg` 更能体现分析师的一致性。

### B. 双重中性化（模板名：双重中性化:以Analyst15为例）
*   **核心结构**: 与上类似，先`ts_backfill(vec_func(Analyst15字段), 60)`，再按国家×行业分组，做组内中性化与时序处理。
*   **思想**: 针对`anl15_*`增长/估值/分红等字段，在截面层面做两次中性化（向量聚合后+组内处理），用于剥离共性行业/国家暴露。
*   **变量要点**: 数据集中`anl15_*`覆盖多期增长率、PE、估值、分红等；`vec_func`与`ts_operator`选择决定信号平滑度；窗口建议60–200以保证填补稳定。
*   **适用场景**: Analyst15预期修正、估值再定价类信号，需要同时消化国家+行业噪音的场景。
*   **逻辑链深度解析**:
    *   **多重剥离**: 彻底消除风格暴露，追求纯 Alpha。
*   **优化方向**:
    *   **顺序**: 先做行业中性，再做国家中性，通常更符合基本面逻辑。

### C. 组间比较（模板名：组间比较_GLB_topdiv）
*   **核心结构**: 先在`country × <group1/>`分组内对回填后的向量聚合结果做`ts_zscore`和`group_zscore`，再计算组均值/极值（`group_min/median/max/sum/count`），用`resid = <compare/>(alpha, alpha_gpm)`求组间残差，最后再做组内+时序处理。
*   **思想**: 对同一层级（如行业/子行业/交易所）之间的相对强弱做剥离，得到“相对组均值”的残差信号，适合跨组对比的Alpha挖掘。
*   **变量要点**: `analyst_field`来源于`fnd8_*`基本面/现金流字段；`vec_op`可选`vec_max/avg/min`；`compare`可用`regression_neut`或`signed_power`提取残差；`t_window`取20/60/200/600，控制平滑与稳定性。
*   **适用场景**: GLB区域的分红/现金流因子（topdiv）在国家+行业框架下的相对价值比较，关注跨组差异的策略。
*   **逻辑链深度解析**:
    *   **相对价值**: 关注的是“我在我的组里是否优秀”，而不是“我绝对值多少”。
*   **优化方向**:
    *   **非线性**: 使用 `rank` 代替原始值计算残差，对异常值更鲁棒。

### D. 组间比较（Analyst15版，模板名：组间比较_glb_topdiv_anl15）
*   **核心结构**: 与上一模板相同，但`analyst_field`替换为`anl15_*`系列的增长/估值/分红字段。
*   **思想**: 通过对Analyst15增长与估值预期的组间残差建模，捕捉行业/国家层面的相对高低估与预期修正。
*   **变量要点**: `group1`可选industry/subindustry/sector/exchange；`compare`与`group_stats`同上；`ts_op`和`group_op`用于残差后再标准化和时序平滑。
*   **适用场景**: 全球范围GLB，基于Analyst15预期数据的组间相对价值或动量信号。
*   **逻辑链深度解析**:
    *   **预期差**: 寻找行业内被分析师低估/高估的股票。
*   **优化方向**:
    *   **时序叠加**: 结合 `ts_delta`，寻找“行业内预期提升最快”的股票。

### E. 顾问分析示例（模板名：顾问分析示例）
*   **核心结构**: `financial_data = ts_backfill(<mixdata/>, 90); gp = industry; <ts_operator/>(<group_operator/>(financial_data, gp), <window/>)`
*   **思想**: 直接对`anl69_*`多字段做90日回填，行业组内标准化后再做时序平滑，生成简洁的行业中性信号。
*   **变量要点**: `mixdata`覆盖`anl69_*`的EPS/EBIT/现金分红/目标价/报告日期等；`ts_operator`可用`ts_zscore`、`ts_scale`、`ts_rank`等；`window`提供60/120/220/600可调节频率。
*   **适用场景**: Analyst69数据驱动的行业内预期跟踪、财报节奏/指引变化监控。
*   **逻辑链深度解析**:
    *   **标准流程**: 填补 -> 截面标准化 -> 时序平滑。这是构建稳健因子的标准三板斧。
*   **优化方向**:
    *   **事件驱动**: 在财报日前后缩短 `ts_mean` 的窗口，提高灵敏度。

"""

class SingleSession(requests.Session):
    _instance = None
    _lock = threading.Lock()
    _relogin_lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if not self._initialized:
            super(SingleSession, self).__init__(*args, **kwargs)
            self._initialized = True

    def get_relogin_lock(self):
        return self._relogin_lock

def load_template_summary(file_path: Optional[str] = None) -> str:
    """
    Loads the template summary from a file or returns the built-in template summary.
    
    Args:
        file_path: Optional path to a .txt or .md file containing the template summary.
                   If None or file doesn't exist, returns the built-in template summary.
    
    Returns:
        str: The template summary content.
    """
    if file_path:
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists() and file_path_obj.is_file():
                with open(file_path_obj, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"✓ 成功从文件加载模板总结: {file_path}")
                    return content
            else:
                print(f"⚠ 警告: 文件不存在: {file_path}，将使用内置模板总结")
        except Exception as e:
            print(f"⚠ 警告: 读取文件时出错: {e}，将使用内置模板总结")
    
    # 返回内置的模板总结
    print("✓ 使用内置模板总结")
    return template_summary


def get_credentials() -> tuple[str, str]:
    """
    Retrieve or prompt for platform credentials.

    This function attempts to read credentials from a JSON file in the user's home directory.
    If the file doesn't exist or is empty, it prompts the user to enter credentials and saves them.

    Returns:
        tuple: A tuple containing the email and password.

    Raises:
        json.JSONDecodeError: If the credentials file exists but contains invalid JSON.
    """
    # 声明使用全局变量
    global username, password
    # please input your own BRAIN Credentials into the function
    return (username, password)

def get_token_from_auth_server() -> str:
    # 声明使用全局变量
    global LLM_API_KEY
    # please input your own LLM Gateway token into the function, please note, we are using kimi-k2-turbo-preview model
    return LLM_API_KEY

def interactive_input() -> dict:
    """
    交互式输入函数，收集所有必要的配置信息。
    
    Returns:
        dict: 包含所有配置信息的字典
    """
    print("\n" + "="*60)
    print("欢迎使用 Alpha Transformer 交互式配置")
    print("此程序在于让您输入一个Alpha ID即可通过历史总结的Alpha模板,转化成更多的表达式")
    print("72变,助您腾云驾雾")
    print("如果你想修改模型，则可以使用新模型的url和api key")
    print("不同模型效果不同，默认的kimi可能会产生语法错误，请检查生成的模板文件进行甄别")
    print("强烈推荐你使用自己总结的模板文档，效果会更好")
    print("="*60 + "\n")
    
    config = {}
    
    # 1. 询问 LLM 模型名称
    print("【1/6】LLM 模型配置")
    print("如果你想修改模型，则可以使用新模型的名称")
    default_model = "kimi-k2-turbo-preview"
    model_input = input(f"请输入 LLM 模型名称 (直接回车使用默认值: {default_model}): ").strip()
    config['LLM_model_name'] = model_input if model_input else default_model
    print(f"✓ LLM 模型名称: {config['LLM_model_name']}\n")
    
    # 2. 询问 LLM API Key
    print("【2/6】LLM API Key 配置")
    api_key = getpass.getpass("请输入 LLM API Key (输入时不会显示): ").strip()
    if not api_key:
        print("⚠ 警告: API Key 为空，程序可能无法正常工作")
    config['LLM_API_KEY'] = api_key
    print("✓ API Key 已设置\n")
    
    # 3. 询问 LLM Base URL
    print("【3/6】LLM Base URL 配置")
    print("提示：不同模型有不同的URL")
    default_url = "https://api.moonshot.cn/v1"
    url_input = input(f"请输入 LLM Base URL (直接回车使用默认值: {default_url}): ").strip()
    config['llm_base_url'] = url_input if url_input else default_url
    print(f"✓ LLM Base URL: {config['llm_base_url']}\n")
    
    # 4. 询问 BRAIN 平台用户名
    print("【4/6】BRAIN 平台认证信息")
    username_input = input("请输入 BRAIN 平台用户名/邮箱: ").strip()
    if not username_input:
        print("⚠ 警告: 用户名为空，程序可能无法正常工作")
    config['username'] = username_input
    print("✓ 用户名已设置\n")
    
    # 5. 询问 BRAIN 平台密码
    password_input = getpass.getpass("请输入 BRAIN 平台密码 (输入时不会显示): ").strip()
    if not password_input:
        print("⚠ 警告: 密码为空，程序可能无法正常工作")
    config['password'] = password_input
    print("✓ 密码已设置\n")
    
    # 6. 询问模板总结文件路径
    print("【5/6】模板总结文件配置")
    print("强烈推荐你使用自己总结的模板文档，效果会更好")
    print("提示: 如果您有 template_summary 的 .txt 或 .md 文件，请输入完整路径")
    print("      如果没有，直接回车将使用内置模板总结")
    template_path = input("请输入模板总结文件路径 (直接回车使用内置模板): ").strip()
    config['template_summary_path'] = template_path if template_path else None
    if template_path:
        print(f"✓ 将尝试从文件加载: {template_path}\n")
    else:
        print("✓ 将使用内置模板总结\n")
    
    # 7. 询问 Alpha ID
    print("【6/7】Alpha ID 配置")
    alpha_id = input("请输入要处理的 Alpha ID: ").strip()
    if not alpha_id:
        print("❌ 错误: Alpha ID 不能为空")
        sys.exit(1)
    config['alpha_id'] = alpha_id
    print(f"✓ Alpha ID: {alpha_id}\n")
    
    # 8. 询问 Top N 参数（仅数据字段）
    print("【7/7】候选数量配置 (Top N)")
    print("提示: 此参数控制为每个占位符生成的数据字段候选数量")
    
    # Datafield top_n
    default_datafield_topn = 50
    datafield_topn_input = input(f"请输入数据字段候选数量 (直接回车使用默认值: {default_datafield_topn}): ").strip()
    try:
        config['top_n_datafield'] = int(datafield_topn_input) if datafield_topn_input else default_datafield_topn
    except ValueError:
        print(f"⚠ 警告: 输入无效，使用默认值: {default_datafield_topn}")
        config['top_n_datafield'] = default_datafield_topn
    print(f"✓ 数据字段候选数量: {config['top_n_datafield']}\n")
    
    print("="*60)
    print("配置完成！开始处理...")
    print("="*60 + "\n")
    
    return config



def expand_dict_columns(data: pd.DataFrame) -> pd.DataFrame:
    """
    Expand dictionary columns in a DataFrame into separate columns.

    Args:
        data (pandas.DataFrame): The input DataFrame with dictionary columns.

    Returns:
        pandas.DataFrame: A new DataFrame with expanded columns.
    """
    dict_columns = list(filter(lambda x: isinstance(data[x].iloc[0], dict), data.columns))
    new_columns = pd.concat(
        [data[col].apply(pd.Series).rename(columns=lambda x: f"{col}_{x}") for col in dict_columns],
        axis=1,
    )

    data = pd.concat([data, new_columns], axis=1)
    return data

def start_session() -> SingleSession:
    """
    Start a new session with the WorldQuant BRAIN platform.

    This function authenticates the user, handles biometric authentication if required,
    and creates a new session.

    Returns:
        SingleSession: An authenticated session object.

    Raises:
        requests.exceptions.RequestException: If there's an error during the authentication process.
    """
    brain_api_url = "https://api.worldquantbrain.com"
    s = SingleSession()
    s.auth = get_credentials()
    r = s.post(brain_api_url + "/authentication")
    print(f"New session created (ID: {id(s)}) with authentication response: {r.status_code}, {r.json()} (新会话已创建)")
    if r.status_code == requests.status_codes.codes.unauthorized:
        if r.headers["WWW-Authenticate"] == "persona":
            print(
                "Complete biometrics authentication and press any key to continue (请完成生物识别认证并按任意键继续): \n"
                + urljoin(r.url, r.headers["Location"])
                + "\n"
            )
            input()
            s.post(urljoin(r.url, r.headers["Location"]))
            while True:
                if s.post(urljoin(r.url, r.headers["Location"])).status_code != 201:
                    input(
                        "Biometrics authentication is not complete. Please try again and press any key when completed (生物识别认证未完成，请重试并按任意键): \n"
                    )
                else:
                    break
        else:
            print("\nIncorrect email or password (邮箱或密码错误)\n")
            return start_session()
    return s

def get_data_categories(s: SingleSession) -> list[dict]:
    """
    Fetch and cache data categories from the BRAIN API.
    """
    global DATA_CATEGORIES
    if DATA_CATEGORIES is not None:
        return DATA_CATEGORIES
    
    try:
        brain_api_url = "https://api.worldquantbrain.com"
        response = s.get(brain_api_url + "/data-categories")
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            DATA_CATEGORIES = data
        elif isinstance(data, dict):
            DATA_CATEGORIES = data.get('results', [])
        else:
            DATA_CATEGORIES = []
        return DATA_CATEGORIES
    except Exception as e:
        print(f"Error fetching data categories: {e}")
        return []

def get_datafields(
    s: SingleSession,
    instrument_type: str = "EQUITY",
    region: str = "USA",
    delay: int = 1,
    universe: str = "TOP3000",
    theme: str = "false",
    dataset_id: str = "",
    data_type: str = "MATRIX",
    search: str = "",
    category: Union[str, list] = "",
) -> pd.DataFrame:
    """
    Retrieve available datafields based on specified parameters.

    Args:
        s (SingleSession): An authenticated session object.
        instrument_type (str, optional): The type of instrument. Defaults to "EQUITY".
        region (str, optional): The region. Defaults to "USA".
        delay (int, optional): The delay. Defaults to 1.
        universe (str, optional): The universe. Defaults to "TOP3000".
        theme (str, optional): The theme. Defaults to "false".
        dataset_id (str, optional): The ID of a specific dataset. Defaults to "".
        data_type (str, optional): The type of data. Defaults to "MATRIX".
        search (str, optional): A search string to filter datafields. Defaults to "".
        category (str or list, optional): A category ID or list of IDs to filter datafields. Defaults to "".

    Returns:
        pandas.DataFrame: A DataFrame containing information about available datafields.
    """
    brain_api_url = "https://api.worldquantbrain.com"
    type_param = f"&type={data_type}" if data_type != "ALL" else ""
    
    url_template = (
        brain_api_url
        + "/data-fields?"
        + f"&instrumentType={instrument_type}"
        + f"&region={region}&delay={str(delay)}&universe={universe}{type_param}&limit=50"
    )
    
    if dataset_id:
        url_template += f"&dataset.id={dataset_id}"
        
    if len(search) > 0:
        url_template += f"&search={search}"
        
    url_template += "&offset={x}"

    count = 0
    if len(search) == 0:
        try:
            count = s.get(url_template.format(x=0)).json()["count"]
        except Exception as e:
            print(f"Error getting count: {e}")
            return pd.DataFrame()
            
        if count == 0:
            print(
                f"No fields found (未找到字段): region={region}, delay={str(delay)}, universe={universe}, "
                f"type={data_type}, dataset.id={dataset_id}"
            )
            return pd.DataFrame()
    else:
        if category:
            count = 500 # Search deeper if filtering
        else:
            count = 100

    max_try = 5
    datafields_list = []
    found_count = 0
    target_found = 50 if category else count

    for x in range(0, count, 50):
        for _ in range(max_try):
            try:
                resp = s.get(url_template.format(x=x))
                if resp.status_code == 200 and "results" in resp.json():
                    datafields = resp
                    break
            except:
                pass
            time.sleep(5)
        else:
            continue

        results = datafields.json().get("results", [])
        if not results:
            break
            
        if category:
            if isinstance(category, list):
                filtered_results = [
                    item for item in results 
                    if isinstance(item.get('category'), dict) and item['category'].get('id') in category
                ]
            else:
                filtered_results = [
                    item for item in results 
                    if isinstance(item.get('category'), dict) and item['category'].get('id') == category
                ]
            datafields_list.append(filtered_results)
            found_count += len(filtered_results)
            if len(search) > 0 and found_count >= target_found:
                break
        else:
            datafields_list.append(results)

    datafields_list_flat = [item for sublist in datafields_list for item in sublist]
    
    if not datafields_list_flat:
        return pd.DataFrame()

    datafields_df = pd.DataFrame(datafields_list_flat)
    datafields_df = expand_dict_columns(datafields_df)
    return datafields_df

def set_alpha_properties(
    s: SingleSession,
    alpha_id: str,
    name: Optional[str] = None,
    color: Optional[str] = None,
    regular_desc: Optional[str] = None,
    selection_desc: str = "None",
    combo_desc: str = "None",
    tags: Optional[list[str]] = None,
) -> requests.Response:
    """
    Update the properties of an alpha.

    Args:
        s (SingleSession): An authenticated session object.
        alpha_id (str): The ID of the alpha to update.
        name (str, optional): The new name for the alpha. Defaults to None.
        color (str, optional): The new color for the alpha. Defaults to None.
        regular_desc (str, optional): Description for regular alpha. Defaults to None.
        selection_desc (str, optional): Description for the selection part of a super alpha. Defaults to "None".
        combo_desc (str, optional): Description for the combo part of a super alpha. Defaults to "None".
        tags (list, optional): List of tags to apply to the alpha. Defaults to None.

    Returns:
        requests.Response: The response object from the API call.
    """
    brain_api_url = "https://api.worldquantbrain.com"
    params = {}
    if name is not None:
        params["name"] = name
    if color is not None:
        params["color"] = color
    if tags is not None:
        params["tags"] = tags
    if regular_desc is not None:
        params.setdefault("regular", {})["description"] = regular_desc
    if selection_desc != "None":  # Assuming "None" is the default string value for selection_desc
        params.setdefault("selection", {})["description"] = selection_desc
    if combo_desc != "None":  # Assuming "None" is the default string value for combo_desc
        params.setdefault("combo", {})["description"] = combo_desc
    
    response = s.patch(brain_api_url + "/alphas/" + alpha_id, json=params)

    return response


def extract_placeholders(template_expression: str) -> list[str]:
    """
    Extracts placeholders from a template expression using regular expressions.
    Placeholders are identified by text enclosed in angle brackets (e.g., `<data_field/>`).
    """
    # Only match placeholders of the form `<name/>` or `<name/>` with alphanumeric and underscores
    return re.findall(r'(<[A-Za-z0-9_]+/>)', template_expression)

def parse_alpha_code(alpha_code: str, all_operators: list[dict]) -> tuple[list[str], list[str]]:
    """
    Parses the alpha code to extract operators and data fields.
    """
    # Remove C-style comments /* ... */
    alpha_code = re.sub(r"/\*[\s\S]*?\*/", "", alpha_code)
    # Remove Python-style comments # ...
    alpha_code = re.sub(r"#.*", "", alpha_code)

    operators_names = [op['name'] for op in all_operators]
    
    found_operators = []
    found_datafields = []

    # Regex to find potential identifiers (operators or datafields)
    # This regex looks for words that could be operators or datafields,
    # excluding numbers and common programming constructs.
    identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', alpha_code)

    for identifier in identifiers:
        if identifier in operators_names:
            found_operators.append(identifier)
        elif not (identifier.isdigit() or identifier.lower() in ['true', 'false', 'null', 'nan', 'if', 'else', 'for', 'while', 'return', 'and', 'or', 'not', 'in', 'is', 'try', 'except', 'finally', 'with', 'as', 'def', 'class', 'import', 'from', 'yield', 'lambda', 'global', 'nonlocal', 'break', 'continue', 'pass', 'async', 'await', 'raise', 'assert', 'del', 'print', 'input', 'len', 'min', 'max', 'sum', 'abs', 'round', 'int', 'float', 'str', 'list', 'dict', 'set', 'tuple', 'range', 'map', 'filter', 'zip', 'open', 'file', 'type', 'id', 'dir', 'help', 'object', 'super', 'issubclass', 'isinstance', 'hasattr', 'getattr', 'setattr', 'delattr', '__import__', 'None', 'True', 'False']):
            found_datafields.append(identifier)
            
    # Remove duplicates
    found_operators = list(set(found_operators))
    found_datafields = list(set(found_datafields))

    return found_operators, found_datafields

async def generate_alpha_description(alpha_id: str, brain_session: SingleSession) -> str:
    """
    Generates and potentially enriches the description of a given Alpha ID from the WorldQuant BRAIN API.

    Args:
        alpha_id (str): The ID of the alpha to retrieve.
        brain_session (SingleSession): The active BRAIN API session.
        llm_client (openai.AsyncOpenAI): The authenticated OpenAI-compatible client.

    Returns:
        str: A JSON string containing the alpha's settings, expression, and potentially enriched description,
             or an empty JSON string if an error occurs.
    """

    async def call_llm_new(prompt: str) -> dict:
        # 声明使用全局变量
        global LLM_model_name, LLM_API_KEY, llm_base_url
        try:
            llm_api_key = get_token_from_auth_server()
            llm_base_url_value = llm_base_url  # 使用全局变量
            llm_client = openai.AsyncOpenAI(base_url=llm_base_url_value, api_key=llm_api_key)
            print("LLM Gateway Authentication successful. (LLM网关认证成功)")
        except Exception as e:
            print(f"LLM Gateway Authentication failed (LLM网关认证失败): {e}")
            sys.exit(1)

        print("--- Calling LLM to propose templates... (正在调用LLM生成模板...) ---")
        try:
            # Await the async create call
            response = await llm_client.chat.completions.create(
                model=LLM_model_name,
                messages=[
                    {"role": "system", "content": "You are a quantitative finance expert and a helpful assistant designed to output JSON."},
                    {"role": "user", "content": prompt},
                ],
                # response_format={"type": "json_object"},
            )

            # The async client may return a nested structure. Try to extract content robustly.
            content = None
            if isinstance(response, dict):
                # Some clients return raw dicts
                # Try common paths
                choices = response.get('choices')
                if choices and isinstance(choices, list):
                    msg = choices[0].get('message') or choices[0]
                    content = msg.get('content') if isinstance(msg, dict) else None
                elif 'content' in response:
                    content = response.get('content')
            else:
                # Fallback: attempt attribute access
                try:
                    content = response.choices[0].message.content
                except Exception:
                    content = None

            if content is None:
                # As a last resort, try to stringify the response
                content = str(response)

            # If content is already a dict/list, return it directly; if it's a JSON string, parse it.
            if isinstance(content, (dict, list)):
                return content
            if isinstance(content, str):
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Return wrapped string if not JSON
                    return {"text": content}

            return {}
        except Exception as e:
            print(f"Error calling LLM (调用LLM出错): {e}")
            return {}

    try:
        brain_api_url = "https://api.worldquantbrain.com"
        alpha_url = f"{brain_api_url}/alphas/{alpha_id}"
        response = brain_session.get(alpha_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        alpha_data = response.json()
        settings = alpha_data.get('settings', {})
        expression_dict = alpha_data.get('regular', alpha_data.get('combo', None))
        
        if not expression_dict or 'code' not in expression_dict:
            print(f"Error: Alpha expression code not found for Alpha ID (未找到Alpha表达式代码): {alpha_id}")
            return json.dumps({})

        alpha_code = expression_dict['code']
        current_description = expression_dict.get('description', '')

        # 1. Get all operators for parsing (no filter as per feedback)
        operators_data = get_brain_operators()
        all_operators = operators_data.get('operators', [])
        
        # 2. Parse the code to get operators and datafields
        found_operators_names, found_datafields_names = parse_alpha_code(alpha_code, all_operators)

        # 3. Get descriptions for operators
        operator_descriptions = {op['name']: op.get('description', 'No description available.') for op in all_operators if op['name'] in found_operators_names}
        
        # 4. Get descriptions for datafields
        datafield_descriptions = {}
        if found_datafields_names:
            # Extract settings from alpha_data for the get_datafields call
            instrument_type = settings.get('instrumentType', 'EQUITY')
            region = settings.get('region', 'USA')
            universe = settings.get('universe', 'TOP3000')
            delay = settings.get('delay', 1)

            for df_name in found_datafields_names:
                # get_datafields returns a DataFrame, so we need to process it
                datafield_df = get_datafields(s=brain_session, instrument_type=instrument_type, region=region, delay=delay, universe=universe, search=df_name)
                if not datafield_df.empty:
                    # Assuming the first result is the most relevant
                    datafield_descriptions[df_name] = datafield_df.iloc[0].get('description', 'No description available.')
                else:
                    datafield_descriptions[df_name] = 'No description found.'
                    
        # 5. Use LLM to judge if current description is good
        judgment_prompt = f"""
        Given the following alpha code, its current description, and descriptions of its operators and datafields:

        Alpha Code:
        {alpha_code}

        Current Description:
        {current_description}

        Operators and their descriptions:
        {json.dumps(operator_descriptions, indent=2)}

        Datafields and their descriptions:
        {json.dumps(datafield_descriptions, indent=2)}

        Alpha Settings:
        {json.dumps(settings, indent=2)}

        Is the current description good enough? Respond with 'yes' or 'no' in a JSON object: {{"judgment": "yes/no"}}
        A "good" description should clearly explain the investment idea, rationale for data used, and rationale for operators used.
        """
        
        judgment_response = await call_llm_new(judgment_prompt)
        is_description_good = judgment_response.get("judgment", "no").lower() == "yes"

        new_description = current_description
        if not is_description_good:
            # 6. If not good, use another LLM to generate a new description
            generation_prompt = f"""
            Based on the following alpha code, its operators, datafields, and settings, generate a new, improved description.
            The description should clearly explain the investment idea, rationale for data used, and rationale for operators used.
            Format the output as:
            "Idea: xxxxx\\nRationale for data used: xxxxx\\nRationale for operators used: xxxxxxx"

            Alpha Code:
            {alpha_code}

            Operators and their descriptions:
            {json.dumps(operator_descriptions, indent=2)}

            Datafields and their descriptions:
            {json.dumps(datafield_descriptions, indent=2)}

            Alpha Settings:
            {json.dumps(settings, indent=2)}
            """
            
            generated_description_response = await call_llm_new(generation_prompt)
            # Assuming LLM returns a string directly or a JSON with a 'description' key
            new_description = generated_description_response.get("description", generated_description_response)
            if isinstance(new_description, dict): # Handle cases where LLM might return a dict directly
                new_description = json.dumps(new_description, indent=2)

            # 7. Override this new description and patch the alpha
            set_alpha_properties(
                s=brain_session,
                alpha_id=alpha_id,
                regular_desc=new_description
            )
            print(f"Alpha {alpha_id} description updated on platform. (Alpha描述已在平台更新)")
            
        if 'regular' in alpha_data:
            alpha_data['regular']['description'] = new_description
        elif 'combo' in alpha_data:
            alpha_data['combo']['description'] = new_description

        return json.dumps({
            'settings': settings,
            'expression': expression_dict
        })

    except requests.exceptions.RequestException as e:
        print(f"Error during API request (API请求出错): {e}")
        return json.dumps({})
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from API. (无法解析API的JSON响应)")
        return json.dumps({})
    except Exception as e:
        print(f"An unexpected error occurred (发生意外错误): {e}")
        return json.dumps({})

def get_brain_operators(scope_filters: Optional[list[str]] = None) -> dict:
    """
    Retrieves the list of available operators from the WorldQuant BRAIN API,
    optionally filtered by a list of scopes. If no scopes are provided, all operators are returned.

    Args:
        scope_filters (list[str], optional): A list of strings to filter operators by their scope (e.g., ["REGULAR", "TS_OPERATOR"]).
                                             If None or empty, all operators are returned.

    Returns:
        dict: A dictionary containing the operators list and count,
              or an empty dictionary if an error occurs.
    """
    try:
        brain_api_url = "https://api.worldquantbrain.com"
        session = start_session()
        operators_url = f"{brain_api_url}/operators"
        response = session.get(operators_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        operators_list = response.json()
        
        if not isinstance(operators_list, list):
            print(f"Error: Expected a list of operators, but received type (预期运算符列表，但收到类型): {type(operators_list)}")
            return {}

        if scope_filters:
            filtered_operators = [
                op for op in operators_list
                if any(s_filter in op.get('scope', []) for s_filter in scope_filters)
            ]
            return {
                'operators': filtered_operators,
                'count': len(filtered_operators)
            }
        else:
            return {
                'operators': operators_list,
                'count': len(operators_list)
            }

    except requests.exceptions.RequestException as e:
        print(f"Error during API request for operators (获取运算符时API请求出错): {e}")
        return {}
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from operators API. (无法解析运算符API的JSON响应)")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred while getting operators (获取运算符时发生意外错误): {e}")
        return {}

async def call_llm(prompt: str, llm_client: openai.AsyncOpenAI, max_retries: int = 3) -> dict:
    """
    Interface with a Large Language Model to process prompts and get a JSON response.
    Includes retry logic for JSON parsing errors.
    """
    # 声明使用全局变量
    global LLM_model_name
    if not llm_client:
        print("LLM client not initialized. Please check authentication. (LLM客户端未初始化，请检查认证)")
        return {}
    
    print("--- Calling LLM... (正在调用LLM...) ---")
    
    for attempt in range(max_retries):
        try:
            response = await llm_client.chat.completions.create(
                model=LLM_model_name,  # Or your preferred model
                messages=[
                    {"role": "system", "content": "You are a quantitative finance expert and a helpful assistant designed to output JSON."},
                    {"role": "user", "content": prompt},
                ],
                # response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            
            # Try to clean markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"⚠ JSON Decode Error (Attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                print(f"❌ Failed to parse JSON after {max_retries} attempts. Raw content: {content[:100]}...")
        except Exception as e:
            print(f"⚠ LLM Call Error (Attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                print(f"❌ Failed to call LLM after {max_retries} attempts.")
        
        # Wait before retrying
        await asyncio.sleep(2)
            
    return {}

async def propose_alpha_templates(alpha_details: dict, template_summary: str, llm_client: openai.AsyncOpenAI) -> dict:
    """
    Uses an LLM to propose new alpha templates based on a seed alpha's details.

    Args:
        alpha_details (dict): The details of the seed alpha.
        template_summary (str): A summary of alpha templates to guide the LLM.
        llm_client (openai.AsyncOpenAI): The authenticated OpenAI-compatible client.

    Returns:
        dict: A dictionary of proposed alpha templates in JSON format.
    """
    if not alpha_details.get('expression'):
        print("Error: Alpha expression is missing. (错误：缺少Alpha表达式)")
        return {}
    else:
        print(f"current seed alpha detail (当前种子Alpha详情): {alpha_details.get('expression')}")
    prompt = f"""
As a world-class BRAIN consultant, your task is to design new alpha templates based on an existing seed alpha.
You will be provided with the seed alpha's expression and a summary of successful alpha templates for inspiration.

**Seed Alpha Expression:**
{alpha_details['expression']}

**Inspiration: Summary of Alpha Templates:**
{template_summary}

**Your Task:**
Based on the structure and potential economic rationale of the seed alpha, by the aid of the Alpha template summary, propose 3-5 new, diverse alpha templates.

**Rules:**
1.  The proposed templates must be valid BRAIN alpha expressions.
2.  Use placeholders like `<data_field/>` for data fields and `<operator/>` for operators that can be programmatically replaced later.
3.  For each proposed template, provide a brief, clear explanation of its investment rationale.
4.  Return the output as a single, valid JSON object where keys are the proposed template strings and values are their corresponding explanations. Do not include any other text or formatting outside of the JSON object.
5.  The proposed new alpha template should be related to the seed Alpha {alpha_details}, either in its format or in economic sense but in different format. utilize the inspiration well.
**Example Output Format:**
{{
  "group_zscore(<ts_rank(<data_field/>, 60)/>, industry)": "A cross-sectional momentum signal, neutralized by industry, to capture relative strength within peer groups.",
  "ts_delta(<data_field/>, 20)": "A simple short-term momentum operator applied to a data field."
}}

Now, generate the JSON object with your proposed templates.
"""

    try:
        # print(f"现在的template summary是{template_summary}")
        proposed_templates = await call_llm(prompt, llm_client)
        return proposed_templates
    except Exception as e:
        print(f"An error occurred while calling the LLM (调用LLM时发生错误): {e}")
        return {}

async def propose_datafield_keywords(template_expression: str, template_explanation: str, placeholder: str, llm_client: openai.AsyncOpenAI) -> list[str]:
    """
    Uses an LLM to propose search keywords for finding data fields.
    """
    prompt = f"""
As a quantitative researcher, you need to find the best data fields for an alpha template placeholder.
Based on the template's logic and the placeholder's name, suggest a list of 3-5 concise search keywords to use with the WorldQuant BRAIN `get_datafields` tool.

**Alpha Template:**
`{template_expression}`

**Template Explanation:**
`{template_explanation}`

**Placeholder to Fill:**
`{placeholder}`

**Your Task:**
Provide a list of search keywords that are likely to yield relevant data fields for this placeholder. The keywords should be specific and diverse. Return the output as a single, valid JSON array of strings.

**Example Input:**
Placeholder: `<slow_moving_characteristic/>`
Explanation: "measures the time-series evolution of a fund's relative rank on a slow-moving characteristic (e.g., fund style, expense tier)"

**Example Output:**
["fund style", "expense ratio", "management fee", "turnover", "aum"]

    Now, generate the JSON array of search keywords for the given placeholder.
"""
    print(f"--- Calling LLM to get keywords for placeholder (正在调用LLM获取占位符关键词): {placeholder} ---")
    response = await call_llm(prompt, llm_client)
    # Accept either a direct list or a dict containing a 'keywords' key
    if isinstance(response, list) and all(isinstance(item, str) for item in response):
        return response
    if isinstance(response, dict):
        # Common keys that might contain the list
        for key in ('keywords', 'data', 'result', 'items'):
            if key in response and isinstance(response[key], list) and all(isinstance(i, str) for i in response[key]):
                return response[key]
    print(f"Warning: LLM did not return a valid list of strings for keywords (警告：LLM未返回有效的关键词列表). Got: {response}")
    return []

async def get_datafield_candidates(s: SingleSession, alpha_details: dict, template_expression: str, template_explanation: str, placeholder: str, llm_client: openai.AsyncOpenAI, top_n: int = 50, user_region: Optional[str] = None, user_universe: Optional[str] = None, user_delay: Optional[int] = None, user_category: Optional[Union[str, list]] = None) -> list[dict]:
    """
    Gets candidate data fields for a placeholder by using an LLM to generate search keywords
    and then calling the BRAIN API's get_datafields to retrieve the top N results for each keyword.
    """
    keywords = await propose_datafield_keywords(template_expression, template_explanation, placeholder, llm_client)
    if not keywords:
        print(f"Could not generate keywords for placeholder (无法生成占位符关键词): {placeholder}")
        return []

    print(f"LLM-proposed keywords for '{placeholder}' (LLM提议的关键词): {keywords}")

    # Extract settings from alpha_details for the get_datafields call
    settings = alpha_details.get('settings', {})
    print(f"Alpha settings for datafield search (用于数据字段搜索的Alpha设置):")
    instrument_type = settings.get('instrumentType', 'EQUITY')
    
    region = user_region if user_region is not None else settings.get('region', 'USA')
    print(f"   数据地区: {region}")
    
    universe = user_universe if user_universe is not None else settings.get('universe', 'TOP3000')
    print(f"   数据范围: {universe}")
    
    delay = user_delay if user_delay is not None else settings.get('delay', 1)
    print(f"   Delay: {delay} 类别")
    
    if user_category:
        print(f"   Category Filter: {user_category}")

    # Use asyncio.gather to make parallel API calls for efficiency
    tasks = []
    for keyword in keywords:
        tasks.append(
            asyncio.to_thread(get_datafields,
                s=s,
                instrument_type=instrument_type,
                region=region,
                delay=delay,
                universe=universe,
                search=keyword,
                category=user_category if user_category else ""
            )
        )
    
    results = await asyncio.gather(*tasks)

    # Process results to get top N from each keyword search
    top_results_per_keyword = []
    for res_df in results:
        if not res_df.empty:
            top_results_per_keyword.append(res_df.head(top_n))

    candidate_datafields = []
    if top_results_per_keyword:
        # Concatenate the top N results from all keywords
        combined_df = pd.concat(top_results_per_keyword, ignore_index=True)
        # Remove duplicates from the combined list
        combined_df.drop_duplicates(subset=['id'], inplace=True)
        # Format the final list of candidates
        candidate_datafields = combined_df[['id', 'description']].to_dict(orient='records')

    return candidate_datafields

async def get_group_datafield_candidates(template_expression: str, template_explanation: str, placeholder: str, llm_client: openai.AsyncOpenAI, top_n: int = 3) -> list[dict]:
    """
    Uses an LLM to select suitable group data fields from a predefined list.
    """
    predefined_group_fields = ["industry", "subindustry", "sector", "market", "exchange"]
    
    prompt = f"""
    As a quantitative researcher, you need to select the most relevant group data fields for an alpha template placeholder.
    Based on the template's logic and the placeholder's name, select {top_n} group fields from the following list that are most suitable: {predefined_group_fields}.
    
    **Alpha Template:**
    `{template_expression}`
    
    **Template Explanation:**
    `{template_explanation}`
    
    **Placeholder to Fill:**
    `{placeholder}`
    
    **Your Task:**
    Provide a list of selected group data fields. Return the output as a single, valid JSON array of strings.
    
    **Example Output Format:**
    ["industry", "sector"]
    
    Now, generate the JSON array of selected group data fields.
    """
    print(f"--- Calling LLM to select group datafields for placeholder (正在调用LLM选择分组数据字段): {placeholder} ---")
    response = await call_llm(prompt, llm_client)
    
    if isinstance(response, list) and all(isinstance(item, str) for item in response):
        return [{"name": field} for field in response[:top_n]]
    print(f"Warning: LLM did not return a valid list of strings for group datafields (警告：LLM未返回有效的分组数据字段列表). Got: {response}")
    return [{"name": field} for field in predefined_group_fields[:top_n]] # Fallback to default if LLM fails

async def get_operator_candidates(template_expression: str, template_explanation: str, placeholder: str, llm_client: openai.AsyncOpenAI, top_n: int = 3) -> list[dict]:
    """
    Gets candidate operators for a placeholder by first fetching all REGULAR scope operators
    and then using an LLM to select the most relevant ones.
    """
    operators_data = get_brain_operators(scope_filters=["REGULAR"])
    all_operators = operators_data.get('operators', [])

    if not all_operators:
        print("No REGULAR scope operators found. (未找到REGULAR范围的运算符)")
        return []

    # Create a summary of available operators for the LLM
    operator_names_and_descriptions = "\n".join([f"- {op['name']}: {op.get('description', 'No description available.')}" for op in all_operators])

    prompt = f"""
    As a quantitative finance expert, you need to select the most relevant operators for an alpha template placeholder.
    Based on the template's logic, its explanation, and the specific placeholder, select {top_n} operators from the provided list that are most suitable.

    **Alpha Template:**
    `{template_expression}`

    **Template Explanation:**
    `{template_explanation}`

    **Placeholder to Fill:**
    `{placeholder}`

    **Available REGULAR Scope Operators:**
    {operator_names_and_descriptions}

    **Your Task:**
    Provide a list of selected operator names. Return the output as a single, valid JSON array of strings.

    **Example Output Format:**
    ["ts_mean", "ts_rank", "ts_decay"]

    Now, generate the JSON array of selected operators.
    """
    print(f"--- Calling LLM to select operator candidates for placeholder (正在调用LLM选择运算符候选): {placeholder} ---")
    response = await call_llm(prompt, llm_client)

    if isinstance(response, list) and all(isinstance(item, str) for item in response):
        # Filter the full list of operators to return the selected ones with their descriptions
        selected_ops_details = []
        for selected_name in response:
            for op in all_operators:
                if op['name'] == selected_name:
                    selected_ops_details.append({"name": op['name'], "description": op.get('description', '')})
                    break
        return selected_ops_details[:top_n]
    
    print(f"Warning: LLM did not return a valid list of strings for operator candidates (警告：LLM未返回有效的运算符候选列表). Got: {response}")
    # Fallback to a default set if LLM fails
    return [{"name": op['name'], "description": op.get('description', '')} for op in all_operators[:top_n]]

async def get_parameter_candidates(param_type: str, template_expression: str, template_explanation: str, placeholder: str, llm_client: openai.AsyncOpenAI) -> list[dict]:
    """
    Uses an LLM to suggest sensible numerical candidates for parameters.
    """
    param_description = "an integer value, typically a window length or count (e.g., `d` in `ts_mean(x, d)`)" if param_type == "integer_parameter" else \
                        "a floating-point number, typically a threshold or factor"

    prompt = f"""
    As a quantitative finance expert, you need to suggest sensible numerical candidates for a placeholder parameter.
    Based on the alpha template's logic, its explanation, and the placeholder's type and context, propose 3-5 diverse numerical candidates.

    **Alpha Template:**
    `{template_expression}`

    **Template Explanation:**
    `{template_explanation}`

    **Placeholder to Fill:**
    `{placeholder}`

    **Parameter Type:**
    This placeholder represents {param_description}.

    **Your Task:**
    Provide a list of numerical candidates that are appropriate for this parameter. Return the output as a single, valid JSON array of numbers.

    **Example Output (for integer_parameter):**
    [10, 20, 60, 120, 252]

    **Example Output (for float_parameter):**
    [0.01, 0.05, 0.1, 0.2, 0.5]

    Now, generate the JSON array of numerical candidates.
    """
    print(f"--- Calling LLM to suggest candidates for {param_type} placeholder (正在调用LLM建议参数候选): {placeholder} ---")
    response = await call_llm(prompt, llm_client)

    if isinstance(response, list) and all(isinstance(item, (int, float)) for item in response):
        return [{"value": val} for val in response]
    print(f"Warning: LLM did not return a valid list of numbers for {param_type} candidates (警告：LLM未返回有效的数字候选列表). Got: {response}")
    
    # Fallback to default if LLM fails
    if param_type == "integer_parameter":
        return [{"value": x} for x in [10, 20, 60, 120, 252]]
    elif param_type == "float_parameter":
        return [{"value": x} for x in [0.01, 0.05, 0.1, 0.2, 0.5]]
    return []

async def judge_placeholder_type(placeholder: str, template_expression: str, template_explanation: str, operator_summary: str, llm_client: openai.AsyncOpenAI) -> str:
    """
    Uses an LLM to judge the type of placeholder (e.g., "data_field", "integer_parameter", "group_operator").
    """
    prompt = f"""
    As a world-class quantitative finance expert, your task is to classify the type of a placeholder within an alpha expression.
    You will be provided with the alpha template, its explanation, the specific placeholder, and a comprehensive summary of available BRAIN operators and data field characteristics.

    **Alpha Template:**
    `{template_expression}`

    **Template Explanation:**
    `{template_explanation}`

    **Placeholder to Classify:**
    `{placeholder}`

    **Available BRAIN Operators and Data Field Characteristics:**
    {operator_summary}

    **Your Task:**
    Classify the `{placeholder}` based on the provided context. The classification should be one of the following types:
    - "data_field": If the placeholder clearly represents a financial data series (e.g., price, volume, fundamental ratio).
    - "group_data_field": If the placeholder represents a categorical field used for grouping or neutralization (e.g., `industry` in `group_zscore(x, industry)`).
    - "operator": If the placeholder represents a BRAIN operator that performs a calculation or transformation.
    - "integer_parameter": If the placeholder represents an integer value, typically a window length or count (e.g., `d` in `ts_mean(x, d)`).
    - "float_parameter": If the placeholder represents a floating-point number, typically a threshold or factor.
    - "string_parameter": If the placeholder represents a string value, like a group name (e.g., `industry` in `group_zscore(x, industry)`).
    - "unknown": If the type cannot be determined from the context.

    Return the classification as a single JSON object with a key "placeholder_type" and its corresponding value. Do not include any other text or formatting outside of the JSON object.

    **Example Output Format:**
    {{"placeholder_type": "data_field"}}
    {{"placeholder_type": "integer_parameter"}}

    Now, classify the placeholder.
    """
    print(f"--- Calling LLM to judge type for placeholder (正在调用LLM判断占位符类型): {placeholder} ---")
    
    response = await call_llm(prompt, llm_client)
    return response.get("placeholder_type", "unknown")

async def populate_template(s: SingleSession, alpha_details: dict, template_expression: str, template_explanation: str, operator_summary: str, llm_client: openai.AsyncOpenAI, top_n_datafield: int = 50, user_region: Optional[str] = None, user_universe: Optional[str] = None, user_delay: Optional[int] = None, user_category: Optional[Union[str, list]] = None) -> dict:
    """
    Populates placeholders in an alpha template with candidate data fields, operators, or parameters.
    """
    placeholders = extract_placeholders(template_expression)
    
    if not placeholders:
        print("No placeholders found in the template. (模板中未找到占位符)")
        return {}

    """
    Populates placeholders in an alpha template with candidate data fields, operators, or parameters.
    """
    placeholders = extract_placeholders(template_expression)
    print(f"Found placeholders in template (在模板中找到占位符): {placeholders}")
    
    populated_placeholders = {}

    for ph in placeholders:
        # Use LLM to judge placeholder type
        ph_type = await judge_placeholder_type(ph, template_expression, template_explanation, operator_summary, llm_client)
        print(f"'{ph}' judged as type (判断类型为): {ph_type}")

        if ph_type == "data_field":
            candidates = await get_datafield_candidates(s, alpha_details, template_expression, template_explanation, ph, llm_client, top_n=top_n_datafield, user_region=user_region, user_universe=user_universe, user_delay=user_delay, user_category=user_category)
            populated_placeholders[ph] = {"type": "data_field", "candidates": candidates}
        elif ph_type == "group_data_field":
            candidates = await get_group_datafield_candidates(template_expression, template_explanation, ph, llm_client)
            populated_placeholders[ph] = {"type": "group_data_field", "candidates": candidates}
        elif ph_type in ["operator", "group_operator", "ts_operator"]:
            candidates = await get_operator_candidates(template_expression, template_explanation, ph, llm_client)
            populated_placeholders[ph] = {"type": ph_type, "candidates": candidates}
        elif ph_type in ["integer_parameter", "float_parameter"]:
            candidates = await get_parameter_candidates(ph_type, template_expression, template_explanation, ph, llm_client)
            populated_placeholders[ph] = {"type": ph_type, "candidates": candidates}
        elif ph_type == "string_parameter":
            # Add logic for string_parameter if needed, for now it returns empty
            populated_placeholders[ph] = {"type": "string_parameter", "candidates": []}
        else:
            print(f"Could not determine type for placeholder (无法确定占位符类型): {ph} (LLM classified as {ph_type})")
            populated_placeholders[ph] = {"type": "unknown", "candidates": []}
            
    return populated_placeholders

def get_datafield_prefix(datafield_name: str) -> str:
    """Extracts the prefix from a datafield name (e.g., 'anl44_...' -> 'anl44')."""
    if '_' in datafield_name:
        return datafield_name.split('_')[0]
    return datafield_name

    

async def generate_new_alphas(alpha_description, brain_session, template_summary: Optional[str] = None, top_n_datafield: int = 50, user_region: Optional[str] = None, user_universe: Optional[str] = None, user_delay: Optional[int] = None, user_category: Optional[Union[str, list]] = None):
    """
    Main function to generate new alpha templates based on a seed alpha.
    
    Args:
        alpha_description: The alpha description JSON string.
        brain_session: The BRAIN session object.
        template_summary: Optional template summary string. If None, will load from built-in.
        top_n_datafield: Number of data field candidates to retrieve (default: 50).
    """
    # 声明使用全局变量
    global LLM_model_name, LLM_API_KEY, llm_base_url
    
    # Load template summary if not provided
    if template_summary is None:
        template_summary = load_template_summary()
    # --- Load Operator Summary ---
    operator_summary = get_brain_operators(scope_filters=["REGULAR"])

    try:
        llm_api_key = get_token_from_auth_server()
        llm_base_url_value = llm_base_url  # 使用全局变量
        llm_client = openai.AsyncOpenAI(base_url=llm_base_url_value, api_key=llm_api_key)
        print("✓ LLM Gateway 认证成功")
    except Exception as e:
        print(f"❌ LLM Gateway 认证失败: {e}")
        sys.exit(1)

    details = json.loads(alpha_description)
    
    if not details:
        print(f"Failed to retrieve details for Alpha (获取Alpha详情失败)")
        sys.exit(1)
    
    print("Alpha Details Retrieved (已获取Alpha详情):")
    print(json.dumps(details, indent=4))


    # --- Step 4: Propose New Alpha Templates ---
    print(f"\n--- Proposing new alpha templates for Alpha (正在为Alpha提议新模板) ---")
    proposed_templates = await propose_alpha_templates(details, template_summary, llm_client)

    if not proposed_templates:
        print("Failed to generate proposed alpha templates. (生成提议模板失败)")
        sys.exit(1)
        
    print("\n--- Proposed Alpha Templates (JSON) (建议的Alpha模板,多样性会受到模型和模板总结文档的影响) ---")
    print(json.dumps(proposed_templates, indent=4))

    # --- Step 5: Process all proposed templates and gather candidates ---
    # --- Step 6: Prepare for Output ---
    # Ensure the output directory exists next to this script
    output_dir = Path(__file__).parent / "output"
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: could not create directory {output_dir}: {e}")

    output_filepath = output_dir / f"Alpha_candidates.json"
    
    final_output = {}
    
    # --- Step 5: Process all proposed templates and gather candidates ---
    for template_expr, template_expl in proposed_templates.items():
        print(f"\n--- Populating template (正在填充模板): '{template_expr}' ---")
        try:
            populated_info = await populate_template(brain_session, details, template_expr, template_expl, operator_summary, llm_client, top_n_datafield=top_n_datafield, user_region=user_region, user_universe=user_universe, user_delay=user_delay, user_category=user_category)
            
            final_output[template_expr] = {
                "template_explanation": template_expl,
                "seed_alpha_settings": details.get('settings', {}),
                "placeholder_candidates": populated_info
            }
            
            # --- Incremental Saving ---
            try:
                with output_filepath.open('w', encoding='utf-8') as f:
                    json.dump(final_output, f, indent=4)
                print(f"✓ Progress saved to {output_filepath.name}")
            except IOError as e:
                print(f"⚠️ Warning: Failed to save progress: {e}")
                
        except Exception as e:
            print(f"❌ Error processing template '{template_expr}': {e}")
            print("Skipping this template and continuing...")
            continue

    print("\n--- Final Consolidated Output (最终合并输出) ---")
    print(json.dumps(final_output, indent=4))


    generated_expressions = set()

    for template_expression, template_data in final_output.items():
        placeholder_candidates = template_data["placeholder_candidates"]
        seed_alpha_settings = template_data["seed_alpha_settings"]

        # Prepare a dictionary to hold lists of candidates for each placeholder
        candidates_for_placeholders = {}
        for placeholder, details in placeholder_candidates.items():
            # Extract only the 'value' or 'name' from the candidates list
            if details["type"] == "data_field":
                candidates_for_placeholders[placeholder] = [c["id"] for c in details["candidates"]]
            elif details["type"] in ["integer_parameter", "float_parameter"]:
                candidates_for_placeholders[placeholder] = [str(c["value"]) for c in details["candidates"]]
            elif details["type"] == "group_data_field":
                candidates_for_placeholders[placeholder] = [c["name"] for c in details["candidates"]]
            elif details["type"] == "operator":
                candidates_for_placeholders[placeholder] = [c["name"] for c in details["candidates"]]
            else:
                candidates_for_placeholders[placeholder] = []


        # --- Step 3: Implement logic to generate all alpha expression combinations from the candidates ---
        # Generate all possible combinations of placeholder values
        placeholder_names = list(candidates_for_placeholders.keys())
        all_combinations_values = list(itertools.product(*candidates_for_placeholders.values()))

        for combination_values in all_combinations_values:
            
            # --- ATOM Mode ---

            datafield_values_in_combo = []
            placeholder_types = {ph: details["type"] for ph, details in placeholder_candidates.items()}
            
            for i, placeholder_name in enumerate(placeholder_names):
                if placeholder_types.get(placeholder_name) == 'data_field':
                    datafield_values_in_combo.append(combination_values[i])
            
            if len(datafield_values_in_combo) > 1:
                first_prefix = get_datafield_prefix(datafield_values_in_combo[0])
                if not all(get_datafield_prefix(df) == first_prefix for df in datafield_values_in_combo):
                    continue  # Skip this combination as prefixes do not match

            current_expression = template_expression
            for i, placeholder_name in enumerate(placeholder_names):
                current_expression = current_expression.replace(placeholder_name, combination_values[i])
            
            # Check for duplicates before adding
            if current_expression not in generated_expressions:
                generated_expressions.add(current_expression)
    # dump all unique generated expressions to a file, a list of strings in json file
    print(f"\n--- Total Unique Generated Alpha Expressions (生成的唯一Alpha表达式总数): {len(generated_expressions)} ---")
    # output_filepath = output_dir / f"Alpha_generated_expressions.json"
    # try:
    #     with output_filepath.open('w', encoding='utf-8') as f:
    #         json.dump(list(generated_expressions), f, indent=4)
    #     print(f"\nGenerated expressions successfully written to {output_filepath} (生成的表达式已成功写入)")
    # except IOError as e:
    #     print(f"Error writing generated expressions to file {output_filepath} (写入生成的表达式出错): {e}")
    
    

    validator = val.ExpressionValidator()
    print("开始表达式语法检查感谢社区贡献，原帖https://support.worldquantbrain.com/hc/en-us/community/posts/36740689434391--check%E7%8E%8B-%E9%AA%8C%E8%AF%81%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%98%AF%E5%90%A6%E6%AD%A3%E7%A1%AE%E7%9A%84%E8%84%9A%E6%9C%AC-%E4%B8%83%E5%8D%81%E4%BA%8C%E5%8F%98%E9%BB%84%E9%87%91%E6%90%AD%E6%A1%A3?page=1#community_comment_36798176158999")
    print("请注意，该文件仅用于验证表达式的格式正确性，\n不保证表达式在实际使用中的逻辑正确性或可执行性。\n")
    print("不在内置函数列表中的operator将无法检查，如有需要，请使用AI按需修改本源代码添加")

    expressions_data = list(generated_expressions)
    # 提取表达式列表
    # 假设JSON文件结构为 {"expressions": ["expr1", "expr2", ...]} 或直接是 ["expr1", "expr2", ...]
    if isinstance(expressions_data, dict) and "expressions" in expressions_data:
        expressions = expressions_data["expressions"]
    elif isinstance(expressions_data, list):
        expressions = expressions_data
    else:
        print("错误: JSON文件格式不正确，需要包含表达式列表")
        return

    # 验证表达式
    valid_expressions = []
    invalid_expressions = []

    print(f"开始验证 {len(expressions)} 个表达式...")
    for i, expr in enumerate(expressions, 1):
        if i % 10 == 0:
            print(f"已验证 {i}/{len(expressions)} 个表达式")
            
        result = validator.check_expression(expr)
        if result["valid"]:
            valid_expressions.append(expr)
        else:
            invalid_expressions.append({"expression": expr, "errors": result["errors"]})

    # 生成输出文件路径
    name = "Alpha_generated_expressions"
    valid_output_path = os.path.join(output_dir, f"{name}_success.json")
    invalid_output_path = os.path.join(output_dir, f"{name}_error.json")

    # 保存结果到JSON文件
    print(f"\n验证完成！")
    print(f"有效表达式: {len(valid_expressions)}")
    print(f"无效表达式: {len(invalid_expressions)}")

    # 保存有效表达式
    try:
        with open(valid_output_path, 'w', encoding='utf-8') as f:
            json.dump(valid_expressions, f, ensure_ascii=False, indent=2)
        print(f"有效表达式已保存到: {valid_output_path}")
    except Exception as e:
        print(f"错误: 保存有效表达式失败 - {e}")

    # 保存无效表达式
    try:
        with open(invalid_output_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_expressions, f, ensure_ascii=False, indent=2)
        print(f"无效表达式已保存到: {invalid_output_path}，文件包含错误详情")
        print("查看该文件，你将获得修改模板的灵感，你可以定位到错误的模板并在APP里修改")
    except Exception as e:
        print(f"错误: 保存无效表达式失败 - {e}")

    print("请注意，该文件仅用于验证表达式的格式正确性，\n不保证表达式在实际使用中的逻辑正确性或可执行性。\n")
    print("不在内置函数列表中的operator将无法检查，如有需要，请使用AI按需修改validator源代码添加")

    print("不同模型效果不同，默认的kimi模型可能会产生Alpha语法错误，请检查生成的模板文件进行甄别")
    print("下一步，请下载已完成的模板，放入APP首页进行解析和语法检查，强烈建议生成表达式后手动尝试回测")


async def main():
    """
    Main execution function.
    """

    # Check for command line argument for config file
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"✓ 已从命令行参数加载配置: {config_path}")
                # Ensure all required fields are present or set defaults
                if 'top_n_datafield' not in config:
                    config['top_n_datafield'] = 50
                if 'template_summary_path' not in config:
                    config['template_summary_path'] = None
            except Exception as e:
                print(f"❌ 加载配置文件失败: {e}")
                sys.exit(1)
        else:
            print(f"❌ 配置文件不存在: {config_path}")
            sys.exit(1)
    else:
        # --- Step 0: 交互式输入收集配置信息 ---
        print("输入回车加载同文件夹下的transformer_config.json文件，否则按其他任意键并回车，进入交互式输入账号信息")
        input_str = input()
        if input_str == "":
            config_path = os.path.join(os.path.dirname(__file__), 'transformer_config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            print("\n" + "="*60)
            print("✓ 已从 transformer_config.json 加载账号配置")
            print("="*60 + "\n")
            
            # 继续交互式输入运行时参数
            # 1. 询问模板总结文件路径
            print("【1/3】模板总结文件配置")
            print("强烈推荐你使用自己总结的模板文档，效果会更好")
            print("提示: 如果您有 template_summary 的 .txt 或 .md 文件，请输入完整路径")
            print("      如果没有，直接回车将使用内置模板总结")
            template_path = input("请输入模板总结文件路径 (直接回车使用内置模板): ").strip()
            config['template_summary_path'] = template_path if template_path else None
            if template_path:
                print(f"✓ 将尝试从文件加载: {template_path}\n")
            else:
                print("✓ 将使用内置模板总结\n")
            
            # 2. 询问 Alpha ID
            print("【2/3】Alpha ID 配置")
            alpha_id = input("请输入要处理的 Alpha ID: ").strip()
            if not alpha_id:
                print("❌ 错误: Alpha ID 不能为空")
                sys.exit(1)
            config['alpha_id'] = alpha_id
            print(f"✓ Alpha ID: {alpha_id}\n")
            
            # 3. 询问 Top N 参数（仅数据字段）
            print("【3/3】候选数量配置 (Top N)")
            print("提示: 此参数控制为每个占位符生成的数据字段候选数量")
            default_datafield_topn = 50
            datafield_topn_input = input(f"请输入数据字段候选数量 (直接回车使用默认值: {default_datafield_topn}): ").strip()
            try:
                config['top_n_datafield'] = int(datafield_topn_input) if datafield_topn_input else default_datafield_topn
            except ValueError:
                print(f"⚠ 警告: 输入无效，使用默认值: {default_datafield_topn}")
                config['top_n_datafield'] = default_datafield_topn
            print(f"✓ 数据字段候选数量: {config['top_n_datafield']}\n")
            
            print("="*60)
            print("配置完成！开始处理...")
            print("="*60 + "\n")
        else:
            config = interactive_input()
    
    # 设置全局变量
    global LLM_model_name, LLM_API_KEY, llm_base_url, username, password
    LLM_model_name = config['LLM_model_name']
    LLM_API_KEY = config['LLM_API_KEY']
    llm_base_url = config['llm_base_url']
    username = config['username']
    password = config['password']
    
    # --- Step 1: 加载模板总结 ---
    template_summary = load_template_summary(config.get('template_summary_path'))
    
    # --- Step 2: 启动 BRAIN 会话 ---
    print("--- 正在启动 BRAIN 会话... ---")
    s = start_session()
    
    # --- Step 3: 认证 LLM Gateway ---
    llm_client = None
    print("--- 正在认证 LLM Gateway... ---")
    try:
        llm_api_key = get_token_from_auth_server()
        llm_base_url_value = llm_base_url
        llm_client = openai.AsyncOpenAI(base_url=llm_base_url_value, api_key=llm_api_key)
        print("✓ LLM Gateway 认证成功")
    except Exception as e:
        print(f"❌ LLM Gateway 认证失败: {e}")
        sys.exit(1)

    # --- Step 4: 获取 Alpha 详情 ---
    alpha_id = config['alpha_id']
    print(f"\n--- 正在获取 Alpha ID: {alpha_id} 的详情... ---")

    # --- Step 4.5: 交互式选择数据字段范围 ---
    if len(sys.argv) > 1:
         user_datafield_config = {
            'user_region': config.get('user_region'),
            'user_universe': config.get('user_universe'),
            'user_delay': config.get('user_delay'),
            'user_category': config.get('user_category')
        }
    else:
        user_datafield_config = interactive_datafield_selection(s)

    details_str = await generate_alpha_description(alpha_id, brain_session=s)
    await generate_new_alphas(
        alpha_description=details_str, 
        brain_session=s, 
        template_summary=template_summary,
        top_n_datafield=config.get('top_n_datafield', 50),
        user_region=user_datafield_config.get('user_region'),
        user_universe=user_datafield_config.get('user_universe'),
        user_delay=user_datafield_config.get('user_delay'),
        user_category=user_datafield_config.get('user_category')
    )
    
def interactive_datafield_selection(s: SingleSession) -> dict:
    """
    Interactively ask the user for datafield search configuration (Region, Universe, Delay).
    """
    print("\n" + "="*60)
    print("【附加配置】数据字段搜索范围配置")
    print("正在获取有效的 Region/Universe/Delay 组合...")
    
    try:
        df = get_instrument_type_region_delay(s)
    except Exception as e:
        print(f"⚠ 获取配置选项失败: {e}")
        print("将使用 Seed Alpha 的默认设置")
        return {}

    # Filter for EQUITY only as per current logic
    df_equity = df[df['InstrumentType'] == 'EQUITY']
    
    if df_equity.empty:
        print("未找到 EQUITY 类型的配置选项。")
        return {}
        
    # 1. Select Region
    regions = df_equity['Region'].unique().tolist()
    print(f"\n可用地区 (Region): {regions}")
    region_input = input(f"请输入地区 (直接回车使用 Seed Alpha 默认值): ").strip()
    
    selected_region = None
    if region_input:
        if region_input in regions:
            selected_region = region_input
        else:
            print(f"⚠ 输入无效，将使用默认值")
    
    # 2. Select Delay
    # If region is selected, filter delays for that region
    if selected_region:
        delays = df_equity[df_equity['Region'] == selected_region]['Delay'].unique().tolist()
    else:
        delays = df_equity['Delay'].unique().tolist()
        
    print(f"\n可用延迟 (Delay): {delays}")
    delay_input = input(f"请输入延迟 (直接回车使用 Seed Alpha 默认值): ").strip()
    
    selected_delay = None
    if delay_input:
        try:
            d_val = int(delay_input)
            if d_val in delays:
                selected_delay = d_val
            else:
                print(f"⚠ 输入不在列表中，将使用默认值")
        except ValueError:
            print(f"⚠ 输入无效，将使用默认值")

    # 3. Select Universe
    # If region and delay are selected, filter universes
    if selected_region and selected_delay is not None:
        subset = df_equity[(df_equity['Region'] == selected_region) & (df_equity['Delay'] == selected_delay)]
        if not subset.empty:
            universes = subset.iloc[0]['Universe']
        else:
            universes = []
    else:
        # Just show all unique universes if we can't filter precisely
        universes = set()
        for u_list in df_equity['Universe']:
            universes.update(u_list)
        universes = list(universes)
        
    print(f"\n可用范围 (Universe): {universes}")
    universe_input = input(f"请输入范围 (直接回车使用 Seed Alpha 默认值): ").strip()
    
    selected_universe = None
    if universe_input:
        if universe_input in universes:
            selected_universe = universe_input
        else:
             print(f"⚠ 输入无效，将使用默认值")
             
    # 4. Select Category
    print("\n正在获取数据类别 (Data Categories)...")
    categories = get_data_categories(s)
    
    selected_category = None
    if categories:
        print("\n可用类别 (Categories):")
        for i, cat in enumerate(categories):
            print(f"{i+1}. {cat['name']} (ID: {cat['id']})")
            
        cat_input = input(f"请输入类别编号或ID (多个用逗号分隔, 直接回车不筛选): ").strip()
        
        if cat_input:
            selected_categories = []
            inputs = [x.strip() for x in cat_input.split(',')]
            
            for inp in inputs:
                # Check if input is an index
                if inp.isdigit():
                    idx = int(inp) - 1
                    if 0 <= idx < len(categories):
                        selected_categories.append(categories[idx]['id'])
                        print(f"已选择类别: {categories[idx]['name']}")
                else:
                    # Check if input is an ID
                    found = False
                    for cat in categories:
                        if cat['id'] == inp:
                            selected_categories.append(cat['id'])
                            print(f"已选择类别: {cat['name']}")
                            found = True
                            break
                    if not found:
                        print(f"⚠ 输入无效: {inp}")
            
            if selected_categories:
                selected_category = selected_categories
            else:
                print(f"⚠ 未选择有效类别，将不筛选类别")
    else:
        print("⚠ 无法获取类别列表，跳过类别选择")

    return {
        'user_region': selected_region,
        'user_universe': selected_universe,
        'user_delay': selected_delay,
        'user_category': selected_category
    }

if __name__ == "__main__":
    # To allow asyncio to run in environments like Jupyter notebooks
    if sys.platform.startswith('win') and sys.version_info[:2] >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())

