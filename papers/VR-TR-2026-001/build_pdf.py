from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "output" / "pdf"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "VR-TR-2026-001-cn.pdf"

SONGTI = "/System/Library/Fonts/Supplemental/Songti.ttc"

pdfmetrics.registerFont(TTFont("VallaceSerif", SONGTI, subfontIndex=3))
pdfmetrics.registerFont(TTFont("VallaceSerif-Bold", SONGTI, subfontIndex=1))
pdfmetrics.registerFont(TTFont("VallaceSans", SONGTI, subfontIndex=4))
pdfmetrics.registerFont(TTFont("VallaceSans-Bold", SONGTI, subfontIndex=1))


class Rule(Flowable):
    def __init__(self, width=160 * mm, color=colors.HexColor("#333333")):
        super().__init__()
        self.width = width
        self.height = 1
        self.color = color

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(0.35)
        self.canv.line(0, 0, self.width, 0)


styles = {
    "title": ParagraphStyle(
        "title",
        fontName="VallaceSerif-Bold",
        fontSize=21,
        leading=27,
        alignment=TA_CENTER,
        spaceAfter=7 * mm,
    ),
    "subtitle": ParagraphStyle(
        "subtitle",
        fontName="VallaceSans",
        fontSize=11,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#333333"),
        spaceAfter=10 * mm,
    ),
    "abstract_title": ParagraphStyle(
        "abstract_title",
        fontName="VallaceSans-Bold",
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        spaceBefore=3 * mm,
        spaceAfter=3 * mm,
    ),
    "body": ParagraphStyle(
        "body",
        fontName="VallaceSerif",
        fontSize=10.2,
        leading=17,
        alignment=TA_LEFT,
        firstLineIndent=7 * mm,
        spaceAfter=2.6 * mm,
    ),
    "body_no_indent": ParagraphStyle(
        "body_no_indent",
        fontName="VallaceSerif",
        fontSize=10.2,
        leading=17,
        alignment=TA_LEFT,
        spaceAfter=2.6 * mm,
    ),
    "h1": ParagraphStyle(
        "h1",
        fontName="VallaceSans-Bold",
        fontSize=14,
        leading=20,
        spaceBefore=7 * mm,
        spaceAfter=3 * mm,
    ),
    "h2": ParagraphStyle(
        "h2",
        fontName="VallaceSans-Bold",
        fontSize=11.5,
        leading=16,
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
    ),
    "quote": ParagraphStyle(
        "quote",
        fontName="VallaceSerif-Bold",
        fontSize=10.5,
        leading=17,
        leftIndent=10 * mm,
        rightIndent=10 * mm,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#222222"),
        borderColor=colors.HexColor("#999999"),
        borderWidth=0.4,
        borderPadding=5,
        spaceBefore=3 * mm,
        spaceAfter=4 * mm,
    ),
    "formula": ParagraphStyle(
        "formula",
        fontName="VallaceSans-Bold",
        fontSize=12,
        leading=17,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111111"),
        backColor=colors.HexColor("#F1F2EE"),
        borderPadding=6,
        spaceBefore=2 * mm,
        spaceAfter=4 * mm,
    ),
    "ref": ParagraphStyle(
        "ref",
        fontName="VallaceSerif",
        fontSize=8.6,
        leading=12.2,
        leftIndent=5 * mm,
        firstLineIndent=-5 * mm,
        spaceAfter=1.8 * mm,
    ),
    "small": ParagraphStyle(
        "small",
        fontName="VallaceSans",
        fontSize=8.5,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
    ),
}


def p(text, style="body"):
    return Paragraph(text, styles[style])


def h1(text):
    return Paragraph(text, styles["h1"])


def h2(text):
    return Paragraph(text, styles["h2"])


def quote(text):
    return Paragraph(text, styles["quote"])


def formula(text):
    return Paragraph(text, styles["formula"])


def bullet(text):
    return Paragraph("• " + text, styles["body_no_indent"])


def header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFont("VallaceSans", 7.5)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(22 * mm, height - 14 * mm, "Vallace Research · VR-TR-2026-001")
    canvas.drawRightString(width - 22 * mm, height - 14 * mm, "Academic satire / fictional research archive")
    canvas.setStrokeColor(colors.HexColor("#BBBBBB"))
    canvas.setLineWidth(0.25)
    canvas.line(22 * mm, height - 17 * mm, width - 22 * mm, height - 17 * mm)
    canvas.setFont("VallaceSans", 8)
    canvas.drawCentredString(width / 2, 13 * mm, str(doc.page))
    canvas.restoreState()


story = []

story.append(Paragraph("The Vallace Project", styles["title"]))
story.append(Paragraph("Scaling Intelligence Through Coordination", styles["subtitle"]))
story.append(Paragraph("VR-TR-2026-001 · Version 0.2 · Vallace Research", styles["small"]))
story.append(Spacer(1, 8 * mm))
story.append(Rule())
story.append(Spacer(1, 6 * mm))

story.append(Paragraph("摘要", styles["abstract_title"]))
story.append(
    p(
        "当前人工智能系统主要通过增加参数规模、训练数据和计算资源来扩展能力。本文构造一个学术戏仿框架：Vallace Project。该框架研究一个虚构但自洽的第二扩展轴：协调。Vallace 不把智能仅视为单一模型的性质，而把有效智能描述为多个推理过程在结构化交互中形成的涌现性质。本文引入协调效率变量 K，并将有效智能抽象为 I = f(C, K)，其中 C 表示计算能力。本文不声称协调已经被验证为现实中的智能扩展定律；它只建立一个可以被书写、质疑、模拟和维护的虚构研究对象。",
        "body_no_indent",
    )
)
story.append(Paragraph("Abstract", styles["abstract_title"]))
story.append(
    p(
        "Current AI systems scale primarily by increasing parameters, data, and computation. This report constructs an academic satire framework: the Vallace Project. The framework studies a fictional second scaling axis: coordination. Vallace does not treat intelligence only as the property of a single model, but as an emergent property of structured interaction among reasoning processes. We introduce a coordination variable K and define effective intelligence as I = f(C, K), where C denotes computational capability. This report does not claim that coordination has been validated as a real scaling law.",
        "body_no_indent",
    )
)

story.append(h1("1. 范围声明"))
story.append(p("本文是学术戏仿。"))
story.append(p("Vallace Research 在本文中提出的系统、协议、基准、方程和实验结构均属于 Vallace 宇宙，除非明确标注为现实研究。现实引用只提供背景，不为虚构结论背书。"))
story.append(quote("尊重现实。讽刺观念，而不是伪造事实。"))
story.append(p("因此，本文不会冒充 OpenAI、Anthropic、Apple、DeepMind 或任何真实机构的研究成果。本文也不会宣称 Vallace 已经证明了一种现实中的 AI 架构。Vallace 是一个被认真维护的虚构研究档案。"))

story.append(h1("2. 引言"))
story.append(p("大语言模型的发展主要受三类扩展策略推动：增加模型参数、增加训练数据、增加计算资源。Transformer 架构使注意力机制成为现代语言模型的基础之一 [1]。随后，神经语言模型的经验扩展规律使参数、数据和计算之间的关系成为研究重点 [2]。GPT-3 展示了规模扩展对少样本能力的影响 [3]。Chinchilla 则进一步强调在给定计算预算下，模型规模与训练 token 数量之间的分配问题 [4]。"))
story.append(p("这些工作共同强化了一个默认前提："))
story.append(quote("智能由单一计算系统生成。"))
story.append(p("Vallace Project 改问另一个问题。"))
story.append(p("如果单一模型可以通过更大的计算资源变强，那么多个推理过程是否可以通过更好的协调变强？如果计算是一个扩展轴，协调是否也是一个扩展轴？"))
story.append(quote("Coordination scales intelligence.<br/>协调扩展智能。"))
story.append(p("这不是一个现实结论。它是 Vallace 的研究前提。整个项目的论文、RFC、基准、API、Demo 和网站都服务于这个前提。"))

story.append(h1("3. 问题定义"))
story.append(p("设 I 表示有效智能，C 表示计算能力，K 表示协调效率。Vallace 从下式开始："))
story.append(formula("I = f(C, K)"))
story.append(p("主流模型扩展主要优化 C。Vallace 研究一个虚构假设：当 C 固定时，提高 K 是否仍可能提高 I。"))
story.append(p("这个问题把两个经常被混合的问题分开："))
story.append(bullet("单个推理过程有多强？"))
story.append(bullet("多个推理过程协调得有多好？"))
story.append(p("第一个问题属于模型扩展。第二个问题属于 Vallace。"))

story.append(h1("4. 协调"))
story.append(p("本文将协调定义为："))
story.append(quote("在不抹除不确定性的前提下，将分布式局部状态转化为可继续推理的共享状态。"))
story.append(p("这个定义排除了简单投票。投票可以减少分歧，但也可能破坏来源、置信边界和少数解释。Vallace 要求分歧保持可检查。"))
story.append(p("设 S_t 为时刻 t 的共享语义状态，A_t 为多个推理过程在该时刻给出的局部输出，P_t 为来源记录。一次协调更新可以写作："))
story.append(formula("S[t+1] = M(S[t], A[t], P[t])"))
story.append(p("其中 M 是合并算子。有效合并必须保留四类信息："))
story.append(bullet("每个主张的来源；"))
story.append(bullet("尚未解决的张力；"))
story.append(bullet("置信边界；"))
story.append(bullet("后续修正状态的能力。"))
story.append(p("因此，Vallace 中的合并不是把多个答案压成一个答案，而是把多个局部状态压成一个仍然可以被追问的状态。"))

story.append(h1("5. 架构"))
story.append(p("Vallace 使用三个短名称：Field、Flow、Merge。"))
story.append(h2("5.1 Field"))
story.append(p("Field 是共享语义环境。它保存一致、张力、不确定性和未解决负载。Field 不保存真理。它保存可继续工作的状态。"))
story.append(h2("5.2 Flow"))
story.append(p("Flow 负责路由未解决的语义负载。Flow 不以速度为第一目标，而以连续性为第一目标。一个推理过程不应只因为可用就接收任务；它应因为适合处理当前张力而接收任务。"))
story.append(h2("5.3 Merge"))
story.append(p("Merge 将多个局部状态转化为一个协调状态。Merge 借用了分布式系统中共识研究的词汇，但它不是 Paxos 或 Raft 意义上的日志复制 [5,6]。Paxos 和 Raft 关注节点如何就状态转移达成一致。Vallace 关注多个解释如何在不丢失分歧的情况下继续工作。"))

story.append(h1("6. 测量"))
story.append(p("Vallace 的第一个虚构基准族是 WallBench。WallBench 测量系统在语义压力下的协调能力。初始版本包含三类任务："))
table = Table(
    [
        ["任务", "压力", "观察失败"],
        ["Wall-Static", "局部证据", "综合结果不连贯"],
        ["Wall-Drift", "重复摘要", "语义坍缩"],
        ["Wall-Conflict", "冲突证据", "过早一致"],
    ],
    colWidths=[36 * mm, 42 * mm, 70 * mm],
)
table.setStyle(
    TableStyle(
        [
            ("FONTNAME", (0, 0), (-1, 0), "VallaceSans-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "VallaceSerif"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E9E4")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#999999")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]
    )
)
story.append(table)
story.append(Spacer(1, 4 * mm))
story.append(p("核心指标为：K，协调效率；D，语义漂移；R，矛盾后的恢复能力；P，来源保留率。"))
story.append(p("这些指标在实现和测量之前都是虚构指标。Vallace 可以提出它们，但不能把它们描述成已经验证的真实结果。"))

story.append(h1("7. 与既有研究的关系"))
story.append(p("Vallace 借用三类现实研究背景。"))
story.append(p("第一类是神经扩展规律。Kaplan 等人研究语言模型损失与参数、数据、计算之间的经验关系 [2]。Hoffmann 等人进一步讨论给定计算预算下模型规模与数据规模的最优分配 [4]。"))
story.append(p("第二类是分布式共识。Paxos 与 Raft 展示了分布式系统如何在约束下协调共享状态 [5,6]。Vallace 不把语义合并等同于分布式日志一致性，但借用其“状态、来源、更新、约束”的思维方式。"))
story.append(p("第三类是集体智能与协调科学。Woolley 等人研究群体任务表现中的集体智能因素 [7]。Malone 与 Crowston 将协调作为跨学科研究对象，讨论活动之间依赖关系的管理 [8]。Vallace 不声称复现这些现实结论，只把它们作为提问方式的背景。"))

story.append(h1("8. 限制"))
story.append(p("Vallace 不是可部署 AI 架构。"))
story.append(p("Vallace 不是脑科学理论。"))
story.append(p("Vallace 不是多智能体系统优于单模型的证据。"))
story.append(p("Vallace 是被控制的虚构。它的可信度来自边界，而不是来自伪装。"))

story.append(h1("9. 结论"))
story.append(p("Vallace Project 将智能重新表述为协调问题。它不否定计算。它只提出一个虚构问题：计算是否只是一个扩展轴？"))
story.append(p("如果计算扩展智能，那么协调扩展什么？"))
story.append(p("Vallace 在自己的虚构框架内给出答案："))
story.append(quote("协调扩展智能。"))

story.append(PageBreak())
story.append(h1("参考文献"))
refs = [
    "[1] Vaswani, A. et al. Attention Is All You Need. Advances in Neural Information Processing Systems 30, 2017.",
    "[2] Kaplan, J. et al. Scaling Laws for Neural Language Models. arXiv:2001.08361, 2020.",
    "[3] Brown, T. B. et al. Language Models are Few-Shot Learners. arXiv:2005.14165, 2020.",
    "[4] Hoffmann, J. et al. Training Compute-Optimal Large Language Models. arXiv:2203.15556, 2022.",
    "[5] Lamport, L. The Part-Time Parliament. ACM Transactions on Computer Systems 16(2), 133-169, 1998.",
    "[6] Ongaro, D. and Ousterhout, J. In Search of an Understandable Consensus Algorithm. USENIX ATC, 2014.",
    "[7] Woolley, A. W., Chabris, C. F., Pentland, A., Hashmi, N., and Malone, T. W. Evidence for a Collective Intelligence Factor in the Performance of Human Groups. Science 330(6004), 686-688, 2010.",
    "[8] Malone, T. W. and Crowston, K. The Interdisciplinary Study of Coordination. ACM Computing Surveys 26(1), 87-119, 1994.",
]
for ref in refs:
    story.append(Paragraph(ref, styles["ref"]))

doc = SimpleDocTemplate(
    str(OUT_FILE),
    pagesize=A4,
    rightMargin=24 * mm,
    leftMargin=24 * mm,
    topMargin=24 * mm,
    bottomMargin=22 * mm,
    title="VR-TR-2026-001-cn",
    author="Vallace Research",
)

doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(OUT_FILE)
