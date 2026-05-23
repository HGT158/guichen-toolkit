# Suresh 等 - 2026 - AgenticRAG Agentic Retrieval for Enterprise Knowledge Bases

_Source PDF: Suresh 等 - 2026 - AgenticRAG Agentic Retrieval for Enterprise Knowledge Bases.pdf_

## Page 1

AgenticRAG: Agentic Retrieval for Enterprise Knowledge Bases
Susheel Suresh*†, Hazel Mak∗‡, Shangpo Chou, Fred Kroon, Sahil Bhatnagar
Microsoft Corporation
Abstract ranking pipelines built on inverted indexes, proba-
bilistic retrieval, and learned ranking models (Liu
We present AgenticRAG, a practical agen- et al., 2009; Nogueira and Cho, 2019; Thakur et al.,
tic harness for retrieval and analysis over en- 2021). These systems excel at keyword and short
terprise knowledge bases. Standard RAG
semantic queries and are strong for high-recall can-2026 pipelines place significant burden of grounding
didate generation. However, they are not designed on the search stack, constraining the language
model to a fixed candidate set chosen deep in to resolve situational, multi-document, or analyt-
the retrieval process. Our approach reduces ically complex information needs—the kinds ofMay
this overdependence by layering a lightweight queries knowledge workers issue against dense cor-
7
harness on top of existing enterprise search in- pora such as technical manuals, compliance docu-
frastructure, equipping a reasoning LLM with ments, and financial reports.
search, find, open, and summarize tools en-
Real-world RAG systems (AzureAISearch) at-
abling the model to iteratively retrieve informa-
tempt to compensate for these limitations through tion, navigate within documents, and analyze
retrieval enhancement techniques such as HyDE[cs.AI] evidence autonomously. On three open bench-
marks we observe substantial gains: 49.6% re- (Gao et al., 2023), multi-query reformulation
call@1 on BRIGHT (+21.8 pp over the best em- (Wang et al., 2023), and adaptive or iterative re-
bedding baseline), 0.96 factuality on WixQA trieval strategies (Trivedi et al., 2023; Jeong et al.,
(+13% relative improvement), and 92% answer 2024). While these methods provide robustness to
correctness on FinanceBench–within 2 pp of query phrasing and higher retrieval coverage, they
oracle access to true evidence. Ablation studies
largely preserve the same architectural assumption:
show that the most significant factor is the shift
retrieval decisions are finalized before substantive from single-shot retrieval to agentic tool use
(5.9× improvement), while multi-query search reasoning begins. The LLM still operates over
and in-document navigation contribute to both a fixed candidate set selected deep in the search
quality and efficiency. We present various de- stack, without the ability to iteratively navigate
sign choices in our agentic harness that were documents, synthesize evidence across sources, or
informed by pre-production deployments. Our reassess results from a higher-level vantage point.
results demonstrate its suitability for real-world
Recent advances in reasoning-capable languagearXiv:2605.05538v1 enterprise production environments.
models have demonstrated strong performance on
planning and iterative external tool use (Yao et al., 1 Introduction
2023; Schick et al., 2023). Rather than hard-coding
Standard retrieval-augmented generation (RAG) retrieval steps, we can empower the model itself
pipelines follow a static retrieve-then-generate to drive the process—deciding what to search for,
paradigm (Lewis et al., 2020). In this design, the which documents warrant deeper investigation, and
search stack effectively determines the final candi- when sufficient evidence has been gathered. This
date set the large language model (LLM) will see relaxes the pressure on the search stack: it only
and the model’s reasoning is constrained to that set. needs to achieve good recall, while the model han-
Modern enterprise-grade search stacks are highly dles the final precision from its broader context. We
optimized for scalability, latency, and multi-stage present AgenticRAG, a practical harness that equips
a reasoning LLM with four tools—search, find,
*Equal contribution.
†sussuresh@microsoft.com open, and summarize—layered on top of existing
‡hazelmak@microsoft.com enterprise search infrastructure. The search tool

## Page 2

delegates to the underlying search stack for broad field has evolved toward Agentic patterns, where
candidate discovery, while find and open serve as autonomous agents (LLMs) dynamically orches-
precision instruments that let the model drill into trate the retrieval process (Singh et al., 2025; Oche
candidate documents via in-document search and et al., 2025). Foundational work in agentic be-
full-content retrieval (with rolling window access). haviors, such as ReAct (Yao et al., 2023) and
To manage the growing context during long reason- Toolformer (Schick et al., 2023), demonstrated
ing chains, the harness monitors token usage and that LLMs could effectively wield external tools
triggers the summarize tool when a threshold is to solve reasoning problems. This paradigm has
reached, allowing the model to consolidate its find- been formalized in systems like Self-RAG (Asai
ings while preserving key references. Our contribu- et al., 2024) and Corrective RAG (Yan et al., 2024),
tion is system-level: a lightweight inference-time which employ self-reflection mechanisms to cri-
tool harness that requires no model fine-tuning, tique retrieved content and trigger fallbacks (e.g.,
custom embedding model, graph construction, or web search) when necessary. Recent approaches
corpus-specific preprocessing beyond indexing doc- propose to integrate retrieval into planning: Plan-
uments into the existing enterprise search backend. RAG (Lee et al., 2024) and Search-o1 (Li et al.,
We evaluate on three benchmarks spanning re- 2025) separate high-level planning from low-level
trieval, enterprise QA, and financial document rea- execution, allowing agents to decompose complex
soning. Our approach achieves 49.6% recall@1 on queries into sub-tasks. Similarly, Search-R1 (Jin
BRIGHT (+21.8 pp over the best embedding base- et al., 2025) uses reinforcement learning to train
line), 0.96 factuality on WixQA (+13% relative), LLMs for autonomous search decisions. While
and 92.00% answer correctness on FinanceBench– effective, many of these systems are designed for
within 2 pp of oracle access. Our method is de- open-domain search or require fine-tuning, rein-
ployed for pre-production evaluation, and learn- forcement learning, or dedicated retrieval policies,
ings from these deployments directly inform our which makes them less directly applicable to propri-
design choices. We provide detailed ablations an- etary enterprise corpora that cannot be exported for
alyzing the contribution of each tool, the effect of training. They can also incur high latency and to-
multi-query search, and model-level differences in ken costs due to recursive reasoning loops (Trivedi
retrieval strategy. et al., 2023).
Another critical limitation in standard RAG
2 Related Work is the "flattening" of documents into disjointed
chunks, which discards valuable structural priors
Retrieval-Augmented Generation (RAG) grounds like headings and document boundaries. RAPTOR
LLM generation in external corpora to mitigate (Sarthi et al., 2024) addresses this by recursively
parametric memory limitations (Lewis et al., 2020; clustering and summarizing text chunks into a tree
Guu et al., 2020). Early approaches focused on structure, enabling retrieval at varying levels of
identifying relevant documents using sparse or abstraction. Similarly, HiQA (Chen et al., 2024)
dense vector retrieval (Khattab and Zaharia, 2020; constructs multi-document hierarchical contexts.
Izacard and Grave, 2021) to enhance performance Graph RAG (Edge et al., 2024; Scaffidi et al., 2025)
on knowledge-intensive NLP tasks. As context approaches seek to build knowledge graphs from
windows expanded, research shifted toward scal- documents to support query-focused summariza-
ing retrieval to trillions of tokens (Borgeaud et al., tion. While powerful for unifying knowledge (Pan
2022) and optimizing in-context learning (Ram et al., 2024; Wang et al., 2024), graph construction
et al., 2023; Shi et al., 2023). Despite these ad- is often computationally prohibitive for dynamic
vancements, standard RAG pipelines often struggle enterprise environments. In contrast, our Agen-
with "long-tail" knowledge and can suffer from hal- tic RAG harness is an inference-time system that
lucinations when retrieval fails (Mallen et al., 2023; leverages a reasoning model with a "search" tool
Gao et al., 2024). Furthermore, static "retrieve- (using a fast enterprise grade search stack) along-
then-generate" paradigms lack the flexibility to side "find" and "open" tools for deeper information
handle complex, multi-hop queries that require it- gathering and reasoning. This positions the contri-
erative information gathering (Jiang et al., 2023; bution as a deployable system integration for en-
Press et al., 2023). terprise file systems: it works with existing search
To address the brittleness of static pipelines, the infrastructure, preserves document access controls,

## Page 3

and avoids extensive pre-computation or retraining.
3 Method
3.1 System Overview
We present an agentic RAG system for enterprise
document search and question answering over large
file systems. Unlike traditional single-pass RAG
pipelines, our system employs an iterative reason-
ing loop where a large language model (LLM) au-
tonomously decides when to search for documents,
drill into specific passages, and retrieve full content
before producing a final answer.
The system addresses several challenges in en-
terprise RAG: (1) multi-step reasoning: complex
queries require information from multiple docu-
ments, (2) context window constraints: accumu-
Figure 1: Agentic loop
lated retrieval results must fit within LLM lim-
its, (3) grounded responses: answers must include
traceable citations to source documents, and (4) 15). When maximum iterations are reached without
multi-turn efficiency: follow-up queries should a final answer, the agent issues a forced completion
reuse previously retrieved content rather than re- request, requiring the model to respond using avail-
executing redundant searches. Our architecture able information. If the token budget is exceeded
supports multiple model families and reuses ex- during execution, the agent triggers context man-
isting search infrastructure for the backend imple- agement (Sec. 3.4) to free space and continues the
mentation of the retrieval tools. By lightweight, loop. For detailed algorithm, see Appendix A.1.
we mean that the harness consists of four tools, re-
quires no model fine-tuning, no graph construction, 3.3 Retrieval Tools
and no custom embedding index beyond the enter- The system provides three retrieval tools enabling
prise search stack already deployed for document hierarchical document exploration (Table 1). The
discovery. Overall the system comprises three main agent decides which to invoke based on current
components: information needs.
1. Agentic Loop: Orchestrates LLM-tool inter- Search performs enterprise-wide document dis-
actions, bounded by maximum iterations. covery by delegating to the existing enterprise
search stack. In the default configuration, the
2. Retrieval Tools: Three tools (search, find, model may issue up to five query reformulations in
open) provide hierarchical access to enterprise one tool call. The tool returns up to 10 results per
documents. A summarize tool for context query, each containing a snippet, title, filename, file
management during long reasoning chains. type, and other available metadata. Results from
multiple queries are combined and deduplicated. 3. Conversation State: Maintains message his-
Each result receives a unique reference ID (for- tory, token accounting, and reference ID map-
mat: turnmsearchn) using a globally incrementing pings that track documents across iterations.
counter, enabling subsequent find and open opera-
3.2 Agentic Loop tions.
The agent processes each query through a bounded Find performs targeted in-document search
iteration loop (Figure 1). Each iteration, upon re- within a single document identified by its refer-
ceiving the current conversation, the agent either ence ID. Given a list of keyword patterns, lexical
selects a tool to call and appends to the conversa- matching is case-insensitive substring matching; an
tion, or returns the final answer with citations. optional semantic find mode can also be enabled.
The loop terminates under two conditions: (1) The tool returns up to 2 matching passages per
the model produces a text response, or (2) the iter- pattern. Results are deduplicated by content and
ation count reaches maximum iterations (default: truncated at a bounded token limit (∼11k tokens).

### Image OCR

#### Image 1 OCR

Conversation state

## Page 4

Find is most useful when the model knows what
to look for, such as a revenue metric or a named
concept inside a long filing.
Open retrieves full document content in a fixed
line window. Each call returns a window of lines
(default: 1,800) starting from either the beginning
(line 0) or a specific line number chosen by the
agent, and a response header indicating the view-
ing range and total document length (e.g., "View-
ing lines [0–1799] of 3000 lines"). To access more
than one portion from a file, the model makes sub-
sequent calls with an explicit line number value.
This enables navigation through documents exceed-
ing the window size while keeping each response
bounded. Open is most useful when the model
knows where to read, such as context around a Figure 2: Example conversation history with context
table, section heading, or line-numbered preview. management via forced summarize tool call.
The system prompt guides effective tool usage. See
Appendix A.2 for details.
files and indexed into the same enterprise search
3.4 Context Management backend used by the search tool. Search returns
snippet previews with metadata and reference IDs,Since retrieval tools can load ∼11k tokens from
and the find and open tools then access full doc-files each time, the context window can be used
ument content through those IDs. Standard pro-up quickly. To manage that, the harness monitors
tocol of using Recall@1 to measure relevance oftoken usage against a 128K-token threshold: it
retrieved documents is adopted (Su et al., 2024).emits an internal warning when the conversation
We instruct the model in AgenticRAG to providereaches 90% of the budget and forces summariza-
relevancy scores for the citations it uses when pro-tion at the threshold. The summarize tool enables
ducing the answer, which induces a ranking overthe model to record current reasoning and desig-
documents for evaluation. We also test our methodnate which references to preserve. The system then
on WixQA (Cohen et al., 2025), which targetsscans tool messages and removes content not asso-
real-world support and troubleshooting enterpriseciated with preserved reference IDs, freeing tokens
scenarios that require multi-document and multi-while retaining cited evidence. This approach ex-
step reasoning for procedural answers. We adopttends effective context capacity. See Figure 2 for
the same LLM based factuality metric defined inan example conversation history before and after
WixQA. Finally, we run evaluations on the popularcontext management.
FinanceBench (Islam et al., 2023) dataset, which
contains financial questions that require deep rea-4 Experiment Setup
soning over large company financial documents.
Our goal is to evaluate AgenticRAG in realistic Our metric here is answer correctness as a proxy
enterprise settings where knowledge workers is- for accurate information retrieval, since questions
sue complex situational queries requiring multi- pertain to single documents. Detailed benchmark
step reasoning over large corpora of long, domain- descriptions, query set and corpus statistics are pre-
specific documents. To this end we adopt the sented in Appendix B.
BRIGHT benchmark (Su et al., 2024) which con-
tains StackExchange questions spanning eight do- 5 Results
mains. We choose to evaluate on the long-context
5.1 Long-Context Retrieval on BRIGHT
setting of BRIGHT, where documents correspond
to entire web pages rather than snippets and the Table 2 presents retrieval performance on the
task is to retrieve the full relevant document(s) for BRIGHT benchmark, showing the best base-
a given query. For our agentic setting, the full line per category. Full results with all models
BRIGHT web pages are converted to document are in Appendix Table 9, including reasoning-

### Image OCR

#### Image 1 OCR

AFTER

## Page 5

Table 1: Retrieval Tool Specifications
Tool Definition Input Output
SEARCH Discover relevant documents from queries Snippets with reference ID and file
entire corpus metadata (≤10 per query)
FIND Locate specific information from sin- reference id, patterns Passages (≤2 per pattern, ≤11k to-
gle document kens total)
OPEN Retrieve windowed full content from reference id, line number (optional) Line-numbered content (≤1800
single document lines)
Table 2: Long-context retrieval performance on unsplit web pages of StackExchange data from BRIGHT benchmark.
Scores are reported in recall@1. Best baseline per category shown; full results in Table 9.
Category Model Bio. Earth. Econ. Psy. Rob. Stack. Sus. Pony Avg.
Sparse BM25 10.7 15.4 10.7 8.4 7.4 22.2 10.7 5.4 11.4
Open-source Emb. Qwen 39.2 36.1 25.7 42.3 21.3 23.5 33.1 1.3 27.8
Proprietary Emb. Voyage 34.4 35.4 26.7 41.6 12.9 12.8 31.1 1.3 24.5
Reasoning Enhanced ReDI 28.4 22.4 21.2 32.0 19.8 36.3 21.7 – 26.0
Ours (AgenticRAG) GPT-5-mini 61.7 48.1 41.4 65.3 39.4 40.6 46.6 4.8 43.5
⌞search, find, open, summ. Claude Sonnet 4.5 62.3 60.0 58.7 67.9 55.0 34.1 51.7 7.1 49.6
enhanced baselines such as LLM re-rankers over WixQA Benchmark ExpertWritten
1.0 Retrieval 0.96BM25/SBERT and ReDI. Our agentic harness BM25 Agentic
E5 0.9 0.85equipped with search, find, open, and summa- 0.83 0.82
rize tools enables both Claude Sonnet 4.5 and 0.8 0.80 0.76 0.76 0.79
0.72 FactualityGPT-5-mini to achieve the highest recall@1 across 0.7
all eight benchmark splits compared to all base- 0.6
lines. With our AgenticRAG retrieval harness, 0.5
Claude Sonnet 4.5 achieves 49.6% average re- Claude3.7Gemini2.0Flash GPT-4o GPT-4oMini GPT-5-mini
call@1 (+21.8 pp over Qwen, the best embedding Generation Model
model at 27.8%) and GPT-5-mini reaches 43.5%
Figure 3: Factuality performance on the WixQA Expert
(+15.7 pp). Gains are consistent across domains, Written dataset (N=200). Our agentic approach (red)
with the largest improvements in Economics (+33.0 substantially outperforms BM25 (blue) and E5 (green)
pp), Earth Science (+24.6 pp), Robotics (+33.7 retrieval baselines across all generation models.
pp), and Psychology (+25.6 pp). Even with a vast
corpus of 5.65K long documents averaging 16K
5.2 Enterprise QA on WixQAtokens each, our method scales by leveraging tradi-
tional retrieval via the search tool, deeper reasoning Figure 3 presents factuality results on the WixQA
enabled by the open / find tools and effective con- benchmark, which requires multi-document anal-
text window management by the summarize tool. ysis to answer enterprise support questions. Se-
The best-performing reasoning-enhanced baseline, mantic embeddings alone fail to capture the cross-
ReDI, uses a fine-tuned Qwen3-8B decomposition document reasoning needed for these queries,
and retrieval-fusion model and achieves 26.0% re- whereas the iterative search and reasoning enabled
call@1 in the BRIGHT long-document setting. Our by our harness excels. On the Expert Written split,
method outperforms it by +23.6 pp (via Claude) our method with GPT-5-mini achieves a factuality
and +17.5 pp (via GPT-5-mini). Static approaches score of 0.96, compared to 0.85 for E5 retrieval and
such as one-time query rewriting or LLM-based re- 0.83 for BM25—a 13% relative improvement over
ranking cannot match the iterative reasoning that the best baseline. We observe similar gains on the
our harness provides, and the gap is evident across Simulated split; see Appendix C.3 for details.
all splits.
5.3 Financial Document QA on FinanceBench
Table 3 presents answer correctness on the Fi-
nanceBench dataset, which evaluates question an-

## Page 6

Table 3: Evaluation results on FinanceBench (N=150). within the 15-iteration budget, averaging 4.48–4.79
tool calls per query. The multi-query ablation pro-
Method Ans. Correct (%)
vides a direct efficiency comparison: the full sys-
Traditional RAG 24.24 tem achieves comparable recall with 4.79 average
Agentic w. keyword search tools tool calls versus 6.79 without multi-query search,
⌞pdfgrep,rga,linux cmd 32.71 a 29% reduction in tool calls.
Golden Evidence + GPT-5-mini
⌞oracle retrieval (full page) 94.00 5.5 Ablation Studies
Ours (AgenticRAG) GPT-5-mini
Single-shot vs Agentic Retrieval. From Table 5 ⌞search, find, open, summ. 92.00
the most significant finding is the dramatic improve-
Ours (AgenticRAG) Claude Sonnet 4.5
⌞search, find, open, summ. 91.78 ment from single-shot search to full agentic tool
use. Single-shot search achieves only 8.41% re-
call@1 on average, while agentic tool use reaches
swering over real-world financial filings. The re- 43.49% with GPT-5-mini and 49.59% with Claude
trieval corpus consists of 84 long financial docu- Sonnet 4.5—representing 5.2× and 5.9× improve-
ments averaging ∼116K tokens each (∼140 pages ments respectively. Notably, the proprietary search
per PDF). Our agentic approach with GPT-5-mini stack behind our search tool trades off raw retrieval
achieves 92.00% correctness, substantially outper- quality for speed, immense scale, and availability
forming both traditional RAG (by 3.8×) and more- compared to the state-of-the-art embedding-based
over, is more general than the agentic tool use base- retrievers in Table 2. However, these quality differ-
line of (Subramanian et al., 2026) (by 2.8×), which ences vanish when our agentic harness is employed
relies on keyword search tools like pdfgrep, rga, with a reasoning language model. The improve-
and Linux commands. We also adopt a baseline ment is consistent across splits (ref. Table 10).
where the ground-truth full-page evidence is pro-
Model Comparison and Tool Usage Patterns.
vided directly to GPT-5-mini, bypassing agentic re-
Claude Sonnet 4.5 achieves a +6.1 pp improvement
trieval entirely. This oracle setting achieves 94.00%
over GPT-5-mini, outperforming on seven of eight
and establishes an upper bound on the model’s rea-
splits (detailed per-split results in Appendix Ta-
soning ability given perfect evidence. Our agentic
ble 10). The two models exhibit distinct strategies
system is within 2 pp of this upper bound which
that reflect an exploration–exploitation trade-off.
demonstrates its effectiveness. Between GPT-5-
Claude favors exploitation: it uses fewer search
mini vs Claude Sonnet 4.5, our harness is equally
calls (2.51 vs 3.39) but opens more documents
effective.
(1.54 vs 1.22) and relies more on semantic find
5.4 Token Cost and Retrieval Efficiency (0.42 vs 0.14, a 3× increase), going deeper into
candidate documents. GPT-5-mini favors explo-
Table 4 quantifies the end-to-end token cost of
ration: it issues more search calls with reformu-
agentic retrieval. We measure total tokens con-
lated queries rather than using in-document find,
sumed across the full interaction, including model
casting a wider net across the corpus. In the
thinking, tool-call arguments, retrieved tool results,
BRIGHT long-document setting, where queries
and final answer generation. On BRIGHT, Agenti-
have only ∼1.9 golden documents on average amid
cRAG averages 52.3K total tokens per query, com-
a large corpus, relevant documents are sparse and
pared to 20.4K for Single-shot Search, a 2.6× to-
broad exploration often surfaces irrelevant results.
ken overhead. This cost yields a disproportion-
ate quality gain: Claude Sonnet 4.5 with Agenti- Failure Patterns. The main observed weakness
cRAG reaches 49.6% recall@1, compared to 8.41% is broad multi-evidence retrieval, especially the
for Single-shot Search, a 5.9× improvement. Fi- Pony split, where each query has ∼6.9 gold
nanceBench is more expensive, averaging 114.8K documents on average compared to ∼1.9 across
tokens per query and a 7.8× ratio over single-shot BRIGHT overall. This setting rewards recovering
search, which reflects deep navigation over long many related documents, whereas our harness is
financial filings. This higher cost is paired with optimized for coarse-to-fine navigation toward a
92.00% answer correctness, close to the 94.00% small number of high-value evidence sources. This
oracle evidence upper bound. Tool usage in Ta- explains why Pony remains difficult for both of our
ble 5 further shows that the system operates well models despite large gains on scientific and tech-

## Page 7

Table 4: Total token usage comparison between AgenticRAG and Single-shot Search across BRIGHT splits and
FinanceBench. All values are averages per query (in thousands) and include system prompt, tool calls, tool results,
and any thinking tokens. Cost ratio is AgenticRAG total tokens divided by Single-shot Search total tokens.
Avg. Total Tokens (K) Cost
Dataset N AgenticRAG Single-shot Ratio
Biology 103 49.2 23.0 2.1×
Earth Science 116 52.9 18.7 2.8×
Economics 103 44.6 21.3 2.1×
Psychology 101 58.2 24.8 2.3×
Robotics 101 56.2 23.1 2.4×
Stack Overflow 117 55.7 15.8 3.5×
Sustainable Living 108 59.3 19.9 3.0×
Pony 112 42.6 17.6 2.4×
BRIGHT Avg. 861 52.3 20.4 2.6×
FinanceBench 150 114.8 14.7 7.8×
Table 5: Ablation study of agentic components averaged across all BRIGHT splits. Performance is measured by
recall (R@k), along with average tool usage and per-tool statistics. Per-split results are in Table 10.
Variant R@1 R@3 Avg. Tools Search Open Find Summ.
Single-shot Search 8.41±4.83 12.90±5.87 1 1 - - -
Claude Sonnet 4.5 49.59±7.79 64.20±7.13 4.48±0.26 2.51±0.19 1.54±0.15 0.42±0.11 0.01±0.02
GPT-5-mini 43.49±8.00 62.53±7.23 4.79±0.71 3.39±0.55 1.22±0.25 0.14±0.08 0.06±0.05
⌞w/o Summarize 43.34±8.07 63.85±7.21 4.92±0.70 3.44±0.54 1.31±0.27 0.16±0.09 -
⌞w/o Semantic Find 46.34±7.97 64.44±7.07 5.02±0.73 3.47±0.55 1.34±0.27 0.17±0.09 0.06±0.05
⌞w/o Multi-query Search 44.84±8.08 62.30±7.26 6.79±0.70 4.38±0.57 2.16±0.27 0.24±0.11 0.03±0.04
nical splits where relevant documents are sparse. Findings from Pre-Production Deployments In
The pattern suggests that future trajectory policies our pre-production evaluation we identified sev-
should better detect broad evidence needs and shift eral design choices that guide the model toward
from depth-first document reading to wider cover- more optimal trajectories: (1) Surfacing docu-
age before final ranking. ment metadata in search results like title, file-
name, and file type helps the model disambiguate
semantically similar snippets and avoid redun-
dant searches; (2) Line-numbered document pre-
Component Contributions. We ablate individ- views lets the model anchor on specific content
ual components using GPT-5-mini to understand and jump to relevant sections in successive open
their contributions. The most notable finding con- calls; (3) Candidate reference retention after
cerns multi-query search. In the default config- summarization in the context window enables the
uration, the model can issue up to 5 queries in model to go deeper on promising candidates via
parallel within a single search tool call, with results open/find, rather than restarting retrieval with re-
de-duped and presented together. Restricting the formulated queries.(4) Having a switcher route
system to single-query search (w/o Multi-query complex, multi-intent queries to our agentic rag
Search, 44.84%), where the model issues only one harness for deeper analysis. Simple queries are
query per search call but receives the same num- routed to traditional rag for faster answers. This is
ber of results, achieves comparable recall@1 to the vital for the tradeoff between user experience, cost,
full system but at the cost of increased tool usage— model availability. We have good early signals of
6.79 average tool calls compared to 4.79 for the this being effective and we continue to pursue this
full system, with notably more search operations hybrid approach.
(4.38 vs 3.39) and document opens (2.16 vs 1.22).
This suggests that multi-query search improves ef- 6 Conclusion
ficiency by finding relevant documents with fewer
iterations. Detailed analysis of these ablations is We presented a practical harness for AgenticRAG
provided in Appendix C.2. that equips reasoning language models with search,

## Page 8

find, open, and summarize tools to autonomously Barkan. 2025. Wixqa: A multi-dataset benchmark
retrieve and reason over large enterprise corpora. for enterprise retrieval-augmented generation. arXiv
preprint arXiv:2505.08643.Across three benchmarks, our approach achieves
49.6% recall@1 on BRIGHT (+21.8 pp over Darren Edge, Ha Trinh, Nuo Cheng, Joshua Bradley,
the best embedding baseline), 0.96 factuality on Alex Chao, Apurva Mody, Steven Truitt, and
Jonathan Larson. 2024. From local to global: AWixQA (+13% relative), and 92.00% answer cor-
graph rag approach to query-focused summarization.
rectness on FinanceBench—within 2 pp of oracle arXiv preprint arXiv:2404.16130.
access. Token analysis shows that these gains re-
quire a moderate 2.6× token overhead on BRIGHT Luyu Gao, Xueguang Ma, Jimmy Lin, and Jamie Callan.
2023. Precise zero-shot dense retrieval without rel-relative to single-shot search, while delivering a
evance labels. In Proceedings of the 61st Annual
5.9× recall@1 improvement. These results demon- Meeting of the Association for Computational Lin-
strate that our harness effectively extracts the value guistics (Volume 1: Long Papers), pages 1762–1777.
of reasoning models for enterprise information re-
Yunfan Gao, Yun Xiong, Xinyu Gao, Kangxiang Jia,
trieval tasks requiring deep, multi-step reasoning. Jinliu Pan, Yuxi Bi, Yi Dai, Jiawei Sun, and Haofen
Future work will focus on large-scale deployment, Wang. 2024. Retrieval-augmented generation for
budget-aware routing between traditional and agen- large language models: A survey. arXiv preprint
tic RAG, deeper failure analysis, ablations over arXiv:2312.10997.
iteration and window-size budgets, and optimizing Kelvin Guu, Kenton Lee, Zora Tung, Panupong Pasu-
retrieval trajectories for fast iterative reasoning via pat, and Ming-Wei Chang. 2020. Realm: Retrieval-
fine tuning. augmented language model pre-training. In Inter-
national Conference on Machine Learning (ICML),
Acknowledgments pages 3929–3938.
Pranab Islam, Anand Kannappan, Douwe Kiela, Re-We thank Eli Coon, Kinfe Mengistu and members
becca Qian, Nino Scherrer, and Bertie Vidgen. 2023.
of the broader Copilot Studio team for feedback Financebench: A new benchmark for financial ques-
and discussions during internal experimentations. tion answering. arXiv preprint arXiv:2311.11944.
Special thanks to James Cai and Alejandro Gutier-
Gautier Izacard and Edouard Grave. 2021. Leveraging
rez Munoz for technical guidance and project spon- passage retrieval with generative models for open do-
sorship. main question answering. In Proceedings of the 16th
Conference of the European Chapter of the Associ-
ation for Computational Linguistics: Main Volume,
References pages 874–880.
Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, and Soyeong Jeong, Jinheon Baek, Sukmin Cho, Sung Ju
Hannaneh Hajishirzi. 2024. Self-rag: Learning to re- Hwang, and Jong C Park. 2024. Adaptive-rag: Learn-
trieve, generate, and critique through self-reflection. ing to adapt retrieval-augmented large language mod-
In International Conference on Learning Representa- els through question complexity. In Proceedings of
tions (ICLR). the 2024 Conference of the North American Chap-
ter of the Association for Computational Linguistics
AzureAISearch. Agentic Retrieval - Azure (NAACL).
AI Search — learn.microsoft.com. https:
//learn.microsoft.com/en-us/azure/search/ Zhengbao Jiang, Frank F Xu, Jun Araki, and Graham
agentic-retrieval-overview. [Accessed Neubig. 2023. Active retrieval augmented generation.
14-02-2026]. arXiv preprint arXiv:2305.06983.
Sebastian Borgeaud, Arthur Mensch, Jordan Hoff- Bowen Jin and 1 others. 2025. Search-r1: Training llms
mann, Trevor Cai, Eliza Rutherford, Katie Milli- to reason and leverage search engines with reinforce-
can, George Bm Van Den Driessche, Jean-Baptiste ment learning. arXiv preprint arXiv:2503.09516.
Lespiau, Bogdan Damoc, Aidan Clark, and 1 others.
2022. Improving language models by retrieving from Omar Khattab and Matei Zaharia. 2020. Colbert: Effi-
trillions of tokens. In International Conference on cient and effective passage search via contextualized
Machine Learning (ICML), pages 2206–2240. late interaction over bert. In Proceedings of the 43rd
International ACM SIGIR Conference on Research
X Chen and 1 others. 2024. Hiqa: A hierarchical contex- and Development in Information Retrieval, pages
tual augmentation rag for multi-documents qa. arXiv 39–48.
preprint arXiv:2402.12345.
M Lee and 1 others. 2024. Planrag: A plan-then-
Dvir Cohen, Lin Burg, Sviatoslav Pykhnivskyi, Hagit retrieval augmented generation for generative large
Gur, Stanislav Kovynov, Olga Atzmon, and Gilad language models as decision makers. In Proceedings

## Page 9

of the 2024 Conference of the North American Chap- Language models can teach themselves to use tools.
ter of the Association for Computational Linguistics In Advances in Neural Information Processing Sys-
(NAACL). tems (NeurIPS).
Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Weijia Shi, Sewon Min, Michihiro Yasunaga, Min-
Petroni, Vladimir Karpukhin, Naman Goyal, Hein- joon Seo, Rich James, Mike Lewis, Luke Zettle-
rich Küttler, Mike Lewis, Wen-tau Yih, Tim Rock- moyer, and Wen-tau Yih. 2023. Replug: Retrieval-
täschel, and 1 others. 2020. Retrieval-augmented augmented black-box language models. arXiv
generation for knowledge-intensive nlp tasks. In Ad- preprint arXiv:2301.12652.
vances in Neural Information Processing Systems
Aditi Singh, Abul Ehtesham, Saket Kumar, and Tala Ta- (NeurIPS), volume 33, pages 9459–9474.
laei Khoei. 2025. Agentic retrieval-augmented gen-
Xiaoxue Li and 1 others. 2025. Search-o1: Agen- eration: A survey on agentic rag. arXiv preprint
tic search-enhanced large reasoning models. arXiv arXiv:2501.09136.
preprint arXiv:2501.05366.
Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi,
Niklas Muennighoff, Han-yu Wang, Haisu Liu, QuanTie-Yan Liu and 1 others. 2009. Learning to rank for
Shi, Zachary S Siegel, Michael Tang, and 1 others. information retrieval. Foundations and Trends® in
2024. Bright: A realistic and challenging bench- Information Retrieval, 3(3):225–331.
mark for reasoning-intensive retrieval. arXiv preprint
Alex Mallen, Akari Asai, Victor Zhong, Rajarshi Das, arXiv:2407.12883.
Daniel Khashabi, and Hannaneh Hajishirzi. 2023.
Shreyas Subramanian, Wale Akinfaderin, Yanyan When not to trust language models: Investigating
Zhang, Ishan Singh, Chris Pecora, Mani Khanuja, effectiveness of parametric and non-parametric mem-
Sandeep Singh, and Maira Ladeira Tanke. 2026. Key- ories. In Proceedings of the 61st Annual Meeting of
word search is all you need: Achieving rag-level per- the Association for Computational Linguistics (Vol-
formance without vector databases using agentic tool ume 1: Long Papers), pages 9802–9822.
use.
Rodrigo Nogueira and Kyunghyun Cho. 2019. Pas-
Nandan Thakur, Nils Reimers, Andreas Rücklé, Ab-
sage re-ranking with bert. arXiv preprint
hishek Srivastava, and Iryna Gurevych. 2021. Beir:
arXiv:1901.04085.
A heterogenous benchmark for zero-shot evalua-
tion of information retrieval models. arXiv preprintAgada Joseph Oche, Ademola Glory Folashade,
arXiv:2104.08663. Tirthankar Ghosal, and Arpan Biswas. 2025. A sys-
tematic review of key retrieval-augmented generation Harsh Trivedi, Niranjan Balasubramanian, Tushar Khot,
(rag) systems: Progress, gaps, and future directions. and Ashish Sabharwal. 2023. Interleaving retrieval
arXiv preprint arXiv:2507.18910. with chain-of-thought reasoning for knowledge-
intensive multi-step questions. In Proceedings ofJeff Z Pan and 1 others. 2024. Unifying large language
the 61st annual meeting of the association for com- models and knowledge graphs: A roadmap. IEEE
putational linguistics (volume 1: long papers), pages Transactions on Knowledge and Data Engineering.
10014–10037.
Ofir Press, Muru Zhang, Sewon Min, Ludwig Schmidt,
Liang Wang, Nan Yang, and Furu Wei. 2023.
Noah A Smith, and Mike Lewis. 2023. Measuring
Query2doc: Query expansion with large language
and narrowing the compositionality gap in language
models. arXiv preprint arXiv:2303.07678.
models. arXiv preprint arXiv:2210.03350.
X Wang and 1 others. 2024. Knowledge graph-
Ori Ram, Yoav Levine, Itay Dalmedigos, Doron Schuh- enhanced retrieval-augmented generation. arXiv
mann, Gadi Sasho, Erez Karpas, Ori Shwartz-Ziv, preprint arXiv:2402.12345.
Nitish Gupta, Yasheng Wu, Kevin Leyton-Brown,
and 1 others. 2023. In-context retrieval-augmented Shi-Qi Yan, Jia-Chen Gu, Yun Zhu, and Zhen-Hua Ling.
language models. arXiv preprint arXiv:2302.00083. 2024. Corrective retrieval augmented generation.
arXiv preprint arXiv:2401.15884.
Parth Sarthi, Salman Abdullah, Aditi Tuli, Shubh
Khanna, Anna Goldie, and Christopher D. Manning. Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak
2024. Raptor: Recursive abstractive processing for Shafran, Karthik Narasimhan, and Yuan Cao. 2023.
tree-organized retrieval. In International Conference React: Synergizing reasoning and acting in language
on Learning Representations (ICLR). models. In International Conference on Learning
Representations (ICLR).
H Scaffidi and 1 others. 2025. Graphrag on techni-
cal documents - impact of knowledge graph schema. A Method Details
Transactions on Graph Data and Knowledge.
A.1 Agentic Loop Algorithm
Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta
Raileanu, Maria Lomeli, Luke Zettlemoyer, Nicola Detailed agentic loop algorithm is shown in Algo-
Cancedda, and Thomas Scialom. 2023. Toolformer: rithm 1.

## Page 10

Algorithm 1 Agentic Loop B Dataset Details
Require: user_query, max_calls, token_threshold
Ensure: Formatted answer with citations B.1 BRIGHT Benchmark
1: conversation.add(user_query)
We adopt the BRIGHT benchmark (Su et al., 2024), 2: for i = 1 to max_calls do
3: if tokens(conversation) ≥token_threshold then which is designed to capture realistic enterprise
4: MANAGECONTEXT( ) ▷Force summarize scenarios of information retrieval. BRIGHT de-
5: end if
6: response ←LLM(conversation, tool_schemas) rives queries from StackExchange posts, reflecting
7: if response.has_tool_calls then human-authored, highly situational and domain-
8: for each tool_call in response.tool_calls do specific information needs. For each query, the cor-
9: result ←EXECUTETOOL(tool_call)
10: conversation.add(tool_call, result) pus contains positive documents cited in top-voted
11: end for answers and verified by human annotators, as well
12: else as negative documents collected via search engine
13: return FORMATANSWER(response.text)
14: end if retrieval. The corpora is normalized web content
15: end for (e.g., Wikipedia pages, blogs, and reports). This
16: return FORCEFINALANSWER( )
construction has shown to yields realistic retrieval
pools with substantial semantic overlap between
A.2 System Instructions for Tool Use relevant and irrelevant documents. We choose to
evaluate on the long-context setting of BRIGHT,Overall instructions include:
where documents correspond to entire web pages
• Search before answering when uncertain. rather than snippets and the task is to retrieve the
• Progressively explore using find or open when full relevant document(s) for a given query. Our
snippets are insufficient. experiments span eight domains: Biology, Earth
• Reuse previous results rather than performing Science, Economics, Psychology, Robotics, Stack
search again. Overflow, Sustainable Living, and Pony. These
• Cite every time when information is used from domains cover a broad range of scientific, tech-
tool outputs. nical, and professional areas commonly encoun-
When to use search: tered in enterprise information retrieval. Across
domains, corpora contain hundreds to thousands of • Primary search tool across enterprise corpus.
documents, with average document lengths ranging • First choice for any work-related query.
from several thousand to over 40k tokens. Queries • When users reference current/changing in-
themselves are also non-trivial in length, with av- formation, enterprise-specific terms, or
erage query sizes exceeding 100 tokens in most acronyms.
domains and reaching several hundred tokens in • To verify details rather than making assump-
technical domains such as Robotics and Stack Over- tions.
flow. Benchmark statistics are detailed in Table 6.
When to use find: We follow the standard evaluation protocol of the
• In-document pattern search for relevant files BRIGHT benchmark and report Recall@1 for long-
from search results. context document retrieval.
• When search results do not give enough de-
B.2 WixQA Benchmark tails.
• To get a focused view of a result in relation to WixQA targets procedural, long-form queries that
certain terms. require multi-step reasoning and specialized enter-
prise vocabulary, closely matching real-world sup-When to use open:
port and troubleshooting scenarios. We utilize both
• Windowed full content retrieval for relevant the subsets in WiXQA for our experiments: Expert
files from search results. Written, containing authentic customer queries with
• When search results snippets are insufficient. step-by-step answers authored and validated by hu-
• To pull in more content from the most promis- man domain experts, and Simulated, derived from
ing results. multi-turn user–chatbot interactions and curated
• Can open multiple search results. into single-turn queries with expert-validated pro-
• Option to choose a line number close to the cedural correctness. A defining characteristic of
relevant content. WixQA is its multi-article dependency, where an-

## Page 11

Table 6: Dataset statistics for the BRIGHT benchmark (Su et al., 2024) long-context splits used in our evaluation.
Split # Query # Docs Avg Query Len Avg Doc Len Avg # Gold Docs
Biology 103 524 115.2 9,422.4 1.3
Earth Science 116 601 109.5 27,312.3 1.6
Economics 103 516 181.5 11,896.4 1.1
Psychology 101 512 149.6 12,411.7 1.1
Robotics 101 508 818.9 14,998.2 1.1
Stack Overflow 117 1,858 478.3 40,759.7 1.1
Sustainable Living 108 554 148.5 12,077.7 1.2
Pony 112 577 102.6 1,361.0 6.9
Total/Avg 861 5,650 263.0 16,279.9 1.9
Table 7: Dataset statistics for the WixQA (Cohen et al., 2025) benchmark (median values).
Dataset # Query # Query Tokens # Answer Tokens Multi-Article %
ExpertWritten 200 19 172 27%
Simulated 200 12 50 14%
swering a query may require retrieving and synthe- uments (averaging ∼143 pages and ∼117K tokens
sizing information from multiple documents. All per PDF), which is representative of enterprise do-
queries are grounded in a shared enterprise-scale mains where knowledge workers routinely work
knowledge base of 6,221 domain-specific help ar- with dense, information-heavy manuals, reports,
ticles, making WixQA well suited for evaluating and regulatory filings. Corpus statistics are pre-
agentic RAG that must coordinate retrieval and rea- sented in Table 8. The evaluation metric we use is
soning over complex, multi-document enterprise answer correctness. LLM as a judge is used for this
corpora. Datasets statistics are presented in 7 process and manual review of the results is also
conducted.
B.3 FinanceBench
C Additional Results
Table 8: FinanceBench (Islam et al., 2023) data statis-
tics. C.1 Full BRIGHT Retrieval Results
Table 9 presents the complete retrieval results on
Statistic Value
the BRIGHT benchmark across all baseline mod-
# Queries 150 els.
# Ground docs 84
Avg. # pages / doc 143
Avg. # tokens / doc 116,715 C.2 Detailed Ablation Analysis
Total tokens 9,804,065 Table 10 provides per-split ablation results across
all BRIGHT domains. Removing the summariza-
FinanceBench (Islam et al., 2023) is a human- tion tool (w/o Summarize, 43.34% avg recall@1)
evaluated benchmark consisting of financial ques- has minimal impact, indicating that this component
tions over public company filings (10-K, 10-Q, 8-K, is rarely needed for the retrieval task. Removing se-
and earnings reports in PDF form). Questions span mantic find (w/o Semantic Find, 46.34%) slightly
metrics-generated and domain-relevant categories: improves average recall@1, likely because the lexi-
metrics-generated questions target specific finan- cal find fallback is sufficient for most in-document
cial line items or ratios that require the model to searches and removing the semantic option reduces
locate the relevant data in the document and often latency, allowing more search iterations within the
perform a calculation, making them straightfor- same compute budget.
ward to verify since each has a single unambiguous
C.3 WixQA Simulated Resultsanswer. Domain-relevant questions require deeper
financial reasoning, such as identifying drivers of As shown in Figure. 4, on simulated questions with
margin changes or assessing capital intensity. Each expert validated ground truth answers i.e. Simu-
query pertains to a single document. We choose lated split of WixQA, our method achieves 0.94
this benchmark because of the large size of its doc- factuality, compared to 0.77 for both E5+GPT-4o

## Page 12

Table 9: Full long-context retrieval performance on unsplit web pages of StackExchange data from BRIGHT
benchmark. Scores are reported in recall@1.
Bio. Earth. Econ. Psy. Rob. Stack. Sus. Pony Avg.
Sparse models
BM25 10.7 15.4 10.7 8.4 7.4 22.2 10.7 5.4 11.4
Open-sourced embedding models
BGE 16.4 27.7 20.9 11.6 10.9 13.3 16.9 0.4 14.8
Inst-L 24.6 29.9 13.1 20.3 12.9 15.0 25.4 3.9 18.1
SBERT 25.6 34.1 18.9 15.8 10.9 15.0 18.0 1.2 17.4
E5 29.9 36.3 26.2 46.7 17.3 14.5 32.2 1.1 25.5
SFR 30.3 37.0 24.3 47.7 17.3 14.5 35.0 2.0 26.0
Inst-XL 21.5 31.0 13.1 20.5 13.9 15.0 20.1 6.0 17.6
GritLM 37.5 40.3 25.7 34.4 17.8 20.1 32.4 0.0 26.0
Qwen 39.2 36.1 25.7 42.3 21.3 23.5 33.1 1.3 27.8
Proprietary embedding models
Cohere 31.5 34.5 18.9 20.5 9.9 15.8 15.2 0.8 18.4
OpenAI 32.1 31.4 23.8 34.2 11.9 10.7 26.3 0.0 21.3
Voyage 34.4 35.4 26.7 41.6 12.9 12.8 31.1 1.3 24.5
Google 30.9 38.0 21.9 30.7 12.9 19.2 25.7 0.3 22.4
Reasoning enhanced methods
Claude-3-Opus (BM25) 26.8 13.5 13.4 28.2 7.9 28.2 11.8 – 18.5
GPT-4 (BM25) 26.8 15.8 10.2 30.7 5.9 26.5 9.7 – 17.9
DeepSeek-R1 (BM25) 26.8 20.0 14.4 30.2 14.9 33.3 10.6 – 21.5
ReDI (BM25) 28.4 22.4 21.2 32.0 19.8 36.3 21.7 – 26.0
Claude-3-Opus (SBERT) 34.8 31.6 21.8 15.8 8.9 15.8 16.6 – 20.8
GPT-4 (SBERT) 37.7 35.3 19.9 18.3 12.4 11.5 22.6 – 22.5
DeepSeek-R1 (SBERT) 35.6 34.8 16.0 15.3 8.9 15.0 19.9 – 20.8
ReDI (SBERT) 36.2 32.8 22.8 20.8 10.9 16.2 22.2 – 23.1
Our Agentic methods (search/find/open)
GPT-5-mini 61.7 48.1 41.4 65.3 39.4 40.6 46.6 4.8 43.5
Claude Sonnet 4.5 62.3 60.0 58.7 67.9 55.0 34.1 51.7 7.1 49.6

## Page 13

Table 10: Per-split ablation study of agentic components on BRIGHT. Performance is measured by recall (R@k),
along with average tool usage and per-tool usage statistics.
Variant R@1 R@3 Avg. Tools Search Open Find Sum.
Bio.
Single-shot Search 10.88±5.70 14.63±6.55 1 1 - - -
Claude Sonnet 4.5 62.34±8.33 80.47±7.19 4.36±0.28 2.12±0.20 1.72±0.14 0.52±0.12 0.01±0.02
GPT-5-mini 61.72±8.66 88.28±5.53 4.54±0.78 3.46±0.60 0.98±0.25 0.09±0.06 0.02±0.03
⌞w/o Summarize 58.16±8.59 83.33±6.68 4.52±0.80 3.38±0.57 1.06±0.30 0.07±0.05 -
⌞w/o Semantic Find 59.43±8.42 86.53±6.31 4.49±0.71 3.32±0.57 1.11±0.28 0.04±0.04 0.02±0.03
⌞w/o Multi-query 60.35±8.86 85.44±6.40 6.63±0.80 4.34±0.64 2.20±0.30 0.09±0.07 -
Earth.
Single-shot Search 7.35±4.48 13.62±6.09 1 1 - - -
Claude Sonnet 4.5 60.01±7.38 78.51±5.99 4.54±0.25 2.28±0.19 1.70±0.14 0.54±0.12 0.01±0.02
GPT-5-mini 48.10±8.02 72.06±7.30 5.06±0.78 3.52±0.60 1.36±0.27 0.12±0.07 0.07±0.05
⌞w/o Summarize 48.44±8.33 72.66±6.93 4.88±0.69 3.36±0.55 1.41±0.27 0.11±0.07 -
⌞w/o Semantic Find 56.10±7.87 75.93±6.25 4.99±0.74 3.41±0.56 1.38±0.28 0.14±0.09 0.06±0.04
⌞w/o Multi-query 54.43±7.73 75.00±6.61 6.81±0.71 4.30±0.58 2.28±0.27 0.20±0.10 0.03±0.04
Econ.
Single-shot Search 17.39±7.61 21.74±8.15 1 1 - - -
Claude Sonnet 4.5 58.74±9.47 68.28±8.74 4.50±0.24 2.37±0.15 1.62±0.16 0.50±0.13 0.01±0.02
GPT-5-mini 41.41±9.60 67.68±9.09 3.65±0.69 2.52±0.51 1.04±0.27 0.06±0.06 0.03±0.03
⌞w/o Summarize 45.96±9.85 72.22±8.84 4.07±0.79 3.05±0.63 0.90±0.26 0.12±0.10 -
⌞w/o Semantic Find 46.00±9.50 67.50±9.25 3.97±0.77 2.99±0.58 0.86±0.25 0.05±0.05 0.07±0.07
⌞w/o Multi-query 42.27±9.54 67.53±9.28 6.32±0.70 4.00±0.59 2.20±0.29 0.12±0.07 -
Psy.
Single-shot Search 4.88±4.27 6.95±5.24 1 1 - - -
Claude Sonnet 4.5 67.86±8.93 83.57±6.99 4.08±0.24 2.08±0.17 1.62±0.15 0.37±0.11 0.01±0.02
GPT-5-mini 65.26±8.95 78.84±7.89 3.87±0.68 2.82±0.54 0.86±0.23 0.07±0.06 0.12±0.07
⌞w/o Summarize 58.95±9.47 81.26±7.63 3.97±0.65 2.89±0.50 1.03±0.27 0.04±0.04 -
⌞w/o Semantic Find 65.26±9.21 83.89±6.89 4.36±0.76 2.89±0.53 1.29±0.31 0.05±0.05 0.12±0.07
⌞w/o Multi-query 67.06±9.42 80.04±8.04 6.51±0.77 4.08±0.65 2.27±0.33 0.13±0.08 0.02±0.03
Rob.
Single-shot Search 10.20±6.12 15.31±7.14 1 1 - - -
Claude Sonnet 4.5 54.95±9.41 71.29±8.66 4.92±0.33 2.97±0.22 1.54±0.16 0.41±0.12 -
GPT-5-mini 39.39±9.34 60.61±9.34 5.22±0.75 3.65±0.56 1.44±0.29 0.13±0.09 -
⌞w/o Summarize 39.80±9.18 63.27±9.44 5.13±0.69 3.54±0.56 1.46±0.29 0.13±0.07 -
⌞w/o Semantic Find 43.68±9.74 65.26±9.21 5.63±0.78 3.78±0.59 1.61±0.30 0.22±0.12 0.02±0.03
⌞w/o Multi-query 46.94±9.69 65.82±9.44 6.95±0.68 4.62±0.58 2.09±0.25 0.24±0.10 -
Stack.
Single-shot Search 7.28±4.61 12.14±6.07 1 1 - - -
Claude Sonnet 4.5 34.05±8.19 43.53±8.62 4.76±0.28 3.31±0.26 1.07±0.15 0.36±0.11 0.02±0.02
GPT-5-mini 40.62±8.71 53.12±8.93 6.03±0.76 4.88±0.65 0.85±0.18 0.25±0.15 0.05±0.05
⌞w/o Summarize 37.84±8.56 54.95±9.01 6.71±0.75 5.11±0.64 1.26±0.21 0.34±0.15 -
⌞w/o Semantic Find 41.52±8.71 54.02±8.93 6.62±0.78 5.20±0.66 1.18±0.21 0.19±0.10 0.05±0.04
⌞w/o Multi-query 33.77±8.55 43.42±8.77 7.93±0.71 6.25±0.63 1.24±0.19 0.43±0.21 -
Sus.
Single-shot Search 8.87±5.51 18.28±7.26 1 1 - - -
Claude Sonnet 4.5 51.65±8.97 69.15±8.19 4.48±0.21 2.32±0.15 1.72±0.14 0.44±0.11 -
GPT-5-mini 46.65±9.19 73.45±8.13 5.01±0.65 2.98±0.45 1.88±0.33 0.09±0.06 0.06±0.05
⌞w/o Summarize 53.25±9.22 76.91±7.54 5.17±0.71 3.13±0.47 1.91±0.34 0.13±0.10 -
⌞w/o Semantic Find 55.53±9.16 75.83±7.96 5.39±0.67 3.14±0.45 2.02±0.33 0.15±0.09 0.08±0.06
⌞w/o Multi-query 50.53±9.54 76.47±8.02 7.25±0.61 4.06±0.51 2.92±0.27 0.23±0.10 0.04±0.05
Pony
Single-shot Search 0.40±0.35 0.52±0.46 1 1 - - -
Claude Sonnet 4.5 7.12±1.63 18.79±2.67 4.22±0.29 2.62±0.19 1.36±0.12 0.25±0.10 -
GPT-5-mini 4.79±1.54 6.20±1.63 4.93±0.58 3.31±0.45 1.35±0.22 0.27±0.11 -
⌞w/o Summarize 4.34±1.38 6.16±1.63 4.89±0.56 3.09±0.42 1.45±0.21 0.35±0.18 -
⌞w/o Semantic Find 3.19±1.18 6.58±1.76 4.72±0.63 3.00±0.44 1.22±0.22 0.50±0.17 -
⌞w/o Multi-query 3.34±1.27 4.66±1.51 5.92±0.63 3.35±0.41 2.07±0.23 0.50±0.17 -

## Page 14

WixQA Benchmark Simulated
1.0 Retrieval
BM25 Agentic 0.94
0.9 E5
0.77 0.76 0.77 0.74 0.74 0.75 Factuality 0.8 0.7 0.66
0.63
0.6
0.5
Claude3.7 Flash GPT-4o GPT-4oMini GPT-5-mini Gemini2.0
Generation Model
Figure 4: Factuality performance on the WixQA Sim-
ulated dataset. The performance gap between agentic
retrieval and traditional methods is even larger on syn-
thetic questions that require more complex reasoning.
and E5+Claude 3.7. The improvement is even more
pronounced on this dataset, with a 22% relative
gain. This suggests that agentic retrieval is partic-
ularly effective when questions require more com-
plex reasoning or multi-hop information gathering.
C.4 Example Conversation
Figure 5 shows an example conversation from the
FinanceBench.
Figure 5: Example conversation from FinanceBench.

### Image OCR

#### Image 1 OCR

by utilizing the line items clearly shown in the income statement."
