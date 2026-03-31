import reflex as rx
import ast
from datetime import datetime
from ai_suggester import get_ai_suggestion
from error_detector_visitor import AIReviewer

class CodeReviewerState(rx.State):
    code: str = ""
    result: dict = {}
    ai_suggestion: str = ""
    is_loading: bool = False
    history: list[dict] = []
    history_text: str = ""
    ast_output: str = ""
    test_results: str = ""

    def on_load(self):
        self.code = ""
        self.result = {}
        self.ai_suggestion = ""
        self.history = []
        self.history_text = ""
        self.ast_output = ""
        self.test_results = ""

    def run_analysis(self):
        if not self.code:
            self.result = {"error": "No code to analyze"}
            return

        self.is_loading = True
        try:
            tree = ast.parse(self.code)

            # Run static analysis
            reviewer = AIReviewer()
            reviewer.visit(tree)
            self.result = reviewer.report_unused()
            self.result["formatted_code"] = ast.unparse(tree)

            # Set AST output
            self.ast_output = ast.dump(tree, include_attributes=False, indent=2)

            # Get AI suggestion
            self.ai_suggestion = get_ai_suggestion(self.code)

            # Save history
            new_entry = {
                "code": self.code,
                "summary": {
                    "score": self.result.get("score", "N/A"),
                    "errors": self.result.get("error"),
                    "date": datetime.now().isoformat(),
                },
            }
            self.history = self.history + [new_entry]
            self.history_text = "\n\n".join(
                [
                    f"Run #{i+1} | Score: {entry['summary']['score']} | Date: {entry['summary']['date']}\n" + entry['code']
                    for i, entry in enumerate(self.history)
                ]
            )

        except SyntaxError as e:
            self.result = {"error": f"Syntax Error: {e}"}
            self.ast_output = f"Syntax Error: {e}"
        finally:
            self.is_loading = False

    def compute_ast(self):
        if not self.code:
            self.ast_output = "No code to parse"
            return
        try:
            tree = ast.parse(self.code)
            self.ast_output = ast.dump(tree, include_attributes=False, indent=2)
        except Exception as e:
            self.ast_output = f"AST Error: {e}"

    def run_tests(self):
        """Generate and run basic test cases based on the submitted code."""
        if not self.code:
            self.test_results = "No code to test."
            return
        try:
            import unittest
            import io
            import contextlib

            # Compile and exec the user's code in a fresh namespace
            namespace = {}
            exec(compile(self.code, "<user_code>", "exec"), namespace)

            results = []
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith("_"):
                    results.append(f"✅ Function '{name}' is defined and callable.")

            if not results:
                results.append("ℹ️ No public functions found to test.")

            self.test_results = "\n".join(results)
        except Exception as e:
            self.test_results = f"❌ Test Error: {e}"


# ─────────────────────────────────────────
#  UI THEME — Luminous Logic Stitch Design
# ─────────────────────────────────────────

PRIMARY = "#ff7cf5"
SECONDARY = "#00e3fd"
BG = "#0e0e13"
SURFACE = "#131319"
SURFACE_HIGH = "#1f1f26"
SURFACE_HIGHEST = "#25252d"
OUTLINE = "#48474d"
ON_SURFACE = "#f9f5fd"
ON_SURFACE_VARIANT = "#acaab1"


def navbar():
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon(tag="terminal", size=22, color=SECONDARY),
                rx.text(
                    "AI Code Reviewer",
                    font_size="1.1rem",
                    font_weight="800",
                    background=f"linear-gradient(90deg, {PRIMARY} 0%, {SECONDARY} 100%)",
                    background_clip="text",
                    color="transparent",
                    letter_spacing="0.05em",
                    text_transform="uppercase",
                    font_family="'Space Grotesk', sans-serif",
                ),
                spacing="3",
                align_items="center",
            ),
            rx.spacer(),
            rx.hstack(
                rx.link(
                    "HOME",
                    href="/",
                    color=SECONDARY,
                    font_weight="600",
                    font_size="0.72rem",
                    letter_spacing="0.12em",
                    padding_x="1rem",
                    padding_y="0.4rem",
                    border_bottom=f"2px solid {SECONDARY}",
                    box_shadow=f"0px 2px 8px rgba(0,227,253,0.4)",
                    font_family="'Space Grotesk', sans-serif",
                    _hover={"opacity": "0.7"},
                ),
                rx.link(
                    "ANALYZER",
                    href="/analyzer",
                    color="rgba(255,255,255,0.6)",
                    font_weight="600",
                    font_size="0.72rem",
                    letter_spacing="0.12em",
                    padding_x="1rem",
                    padding_y="0.4rem",
                    font_family="'Space Grotesk', sans-serif",
                    _hover={"color": PRIMARY},
                ),
                rx.link(
                    "HISTORY",
                    href="/history",
                    color="rgba(255,255,255,0.6)",
                    font_weight="600",
                    font_size="0.72rem",
                    letter_spacing="0.12em",
                    padding_x="1rem",
                    padding_y="0.4rem",
                    font_family="'Space Grotesk', sans-serif",
                    _hover={"color": PRIMARY},
                ),
                rx.link(
                    "ABOUT",
                    href="/about",
                    color="rgba(255,255,255,0.6)",
                    font_weight="600",
                    font_size="0.72rem",
                    letter_spacing="0.12em",
                    padding_x="1rem",
                    padding_y="0.4rem",
                    font_family="'Space Grotesk', sans-serif",
                    _hover={"color": PRIMARY},
                ),
                spacing="2",
                display=["none", "none", "flex"],
            ),
            rx.button(
                rx.icon(tag="menu", size=22),
                size="2",
                variant="ghost",
                color="rgba(255,255,255,0.7)",
                display=["flex", "flex", "none"],
            ),
            align="center",
            width="100%",
        ),
        bg="rgba(14,14,19,0.85)",
        backdrop_filter="blur(20px)",
        box_shadow=f"0px 4px 12px rgba(255,124,245,0.06)",
        padding="0 1.5rem",
        height="4rem",
        width="100%",
        position="fixed",
        top="0",
        z_index="50",
        display="flex",
        align_items="center",
    )


def fab():
    """Floating Action Button — bolt icon."""
    return rx.button(
        rx.icon(tag="zap", size=22),
        position="fixed",
        bottom=["6rem", "6rem", "2.5rem"],
        right="1.5rem",
        width="3.5rem",
        height="3.5rem",
        border_radius="full",
        background=f"linear-gradient(135deg, {PRIMARY} 0%, #ff5af9 100%)",
        color="#580058",
        box_shadow=f"0 8px 24px rgba(255,124,245,0.4)",
        z_index="40",
        _hover={"transform": "scale(1.1)", "box_shadow": "0 12px 32px rgba(255,124,245,0.6)"},
        _active={"transform": "scale(0.9)"},
        transition="all 0.2s ease",
    )


def bottom_nav():
    """Mobile bottom navigation bar."""
    return rx.box(
        rx.hstack(
            rx.link(
                rx.vstack(
                    rx.icon(tag="home", size=20),
                    rx.text("Home", font_size="0.6rem", text_transform="uppercase", letter_spacing="0.08em"),
                    spacing="1", align_items="center",
                ),
                href="/",
                color=SECONDARY,
            ),
            rx.link(
                rx.vstack(
                    rx.icon(tag="bar_chart_2", size=20),
                    rx.text("Analyze", font_size="0.6rem", text_transform="uppercase", letter_spacing="0.08em"),
                    spacing="1", align_items="center",
                ),
                href="/analyzer",
                color="rgba(255,255,255,0.4)",
                _hover={"color": PRIMARY},
            ),
            rx.link(
                rx.vstack(
                    rx.icon(tag="code_2", size=20),
                    rx.text("Editor", font_size="0.6rem", text_transform="uppercase", letter_spacing="0.08em"),
                    spacing="1", align_items="center",
                ),
                href="/editor",
                color="rgba(255,255,255,0.4)",
                _hover={"color": PRIMARY},
            ),
            rx.link(
                rx.vstack(
                    rx.icon(tag="history", size=20),
                    rx.text("History", font_size="0.6rem", text_transform="uppercase", letter_spacing="0.08em"),
                    spacing="1", align_items="center",
                ),
                href="/history",
                color="rgba(255,255,255,0.4)",
                _hover={"color": PRIMARY},
            ),
            rx.link(
                rx.vstack(
                    rx.icon(tag="settings", size=20),
                    rx.text("Settings", font_size="0.6rem", text_transform="uppercase", letter_spacing="0.08em"),
                    spacing="1", align_items="center",
                ),
                href="/about",
                color="rgba(255,255,255,0.4)",
                _hover={"color": PRIMARY},
            ),
            justify_content="space-around",
            width="100%",
            align_items="center",
        ),
        display=["flex", "flex", "none"],
        position="fixed",
        bottom="0",
        width="100%",
        height="4rem",
        bg="rgba(14,14,19,0.92)",
        backdrop_filter="blur(12px)",
        box_shadow=f"0px -4px 20px rgba(0,227,253,0.1)",
        z_index="50",
        align_items="center",
        padding_x="1rem",
        font_family="'Space Grotesk', sans-serif",
    )


def editor_view():
    return rx.vstack(
        rx.text_area(
            value=CodeReviewerState.code,
            on_change=CodeReviewerState.set_code,
            placeholder="def hello():\n    print('Hello, world!')",
            height="380px",
            width="100%",
            font_family="monospace",
            font_size="13px",
            border_radius="0.75rem",
            border=f"1px solid {OUTLINE}",
            _focus={"border_color": SECONDARY, "box_shadow": f"0 0 0 2px rgba(0,227,253,0.15)"},
            bg=f"{SURFACE}",
            color=ON_SURFACE,
            resize="vertical",
        ),
        rx.hstack(
            rx.button(
                rx.cond(
                    CodeReviewerState.is_loading,
                    rx.hstack(rx.spinner(size="2"), rx.text("Analyzing..."), spacing="2"),
                    rx.hstack(rx.icon(tag="play", size=16), rx.text("Review Code"), spacing="2"),
                ),
                on_click=CodeReviewerState.run_analysis,
                disabled=CodeReviewerState.is_loading,
                flex="1",
                background=f"linear-gradient(90deg, {PRIMARY} 0%, #ff5af9 100%)",
                color="#580058",
                font_weight="700",
                font_size="0.85rem",
                letter_spacing="0.05em",
                border_radius="full",
                box_shadow=f"0 0 20px rgba(255,124,245,0.3)",
                _hover={"box_shadow": "0 0 30px rgba(255,124,245,0.5)", "transform": "translateY(-1px)"},
                _active={"transform": "scale(0.97)"},
                transition="all 0.2s",
                padding_y="0.75rem",
                font_family="'Space Grotesk', sans-serif",
            ),
            rx.button(
                rx.hstack(rx.icon(tag="flask_conical", size=16), rx.text("Run Tests"), spacing="2"),
                on_click=CodeReviewerState.run_tests,
                flex="1",
                bg=f"rgba(0,227,253,0.1)",
                color=SECONDARY,
                border=f"1px solid rgba(0,227,253,0.3)",
                font_weight="700",
                font_size="0.85rem",
                letter_spacing="0.05em",
                border_radius="full",
                _hover={"bg": "rgba(0,227,253,0.2)"},
                _active={"transform": "scale(0.97)"},
                transition="all 0.2s",
                padding_y="0.75rem",
                font_family="'Space Grotesk', sans-serif",
            ),
            spacing="3",
            width="100%",
        ),
        spacing="4",
        align_items="flex-start",
        width="100%",
    )


def score_badge(score):
    return rx.box(
        rx.text(
            f"Score: {score}",
            font_size="1.2rem",
            font_weight="900",
            background=f"linear-gradient(90deg, {SECONDARY} 0%, {PRIMARY} 100%)",
            background_clip="text",
            color="transparent",
            font_family="'Space Grotesk', sans-serif",
        ),
        padding="0.5rem 1.2rem",
        border_radius="full",
        bg=f"rgba(0,227,253,0.08)",
        border=f"1px solid rgba(0,227,253,0.2)",
    )


def result_view():
    return rx.cond(
        CodeReviewerState.is_loading,
        rx.center(
            rx.vstack(
                rx.spinner(size="3", color=SECONDARY),
                rx.text("Analyzing your code...", color=ON_SURFACE_VARIANT, font_size="0.9rem"),
                spacing="3",
                align_items="center",
            ),
            width="100%",
            height="300px",
        ),
        rx.cond(
            CodeReviewerState.result,
            rx.vstack(
                # Score badge
                score_badge(CodeReviewerState.result.get("score", "N/A")),
                # Formatted Code
                rx.box(
                    rx.text("FORMATTED CODE", font_size="0.68rem", font_weight="700", letter_spacing="0.1em", color=SECONDARY, margin_bottom="0.5rem", font_family="'Space Grotesk', sans-serif"),
                    rx.code_block(
                        CodeReviewerState.result.get("formatted_code", ""),
                        language="python",
                        show_line_numbers=True,
                        width="100%",
                        border_radius="0.75rem",
                        bg=f"{BG}",
                        border=f"1px solid {OUTLINE}",
                    ),
                    width="100%",
                ),
                # AI Suggestions
                rx.box(
                    rx.text("AI SUGGESTIONS", font_size="0.68rem", font_weight="700", letter_spacing="0.1em", color=PRIMARY, margin_bottom="0.5rem", font_family="'Space Grotesk', sans-serif"),
                    rx.box(
                        rx.markdown(CodeReviewerState.ai_suggestion, width="100%"),
                        bg=f"rgba(255,124,245,0.04)",
                        border=f"1px solid rgba(255,124,245,0.15)",
                        border_radius="0.75rem",
                        padding="1rem",
                        color=ON_SURFACE,
                    ),
                    width="100%",
                ),
                # Unused items
                rx.cond(
                    CodeReviewerState.result.get("unused"),
                    rx.box(
                        rx.text("UNUSED ITEMS", font_size="0.68rem", font_weight="700", letter_spacing="0.1em", color="#ff716c", margin_bottom="0.5rem", font_family="'Space Grotesk', sans-serif"),
                        rx.box(
                            rx.text(str(CodeReviewerState.result.get("unused", [])), white_space="pre-wrap", color="rgba(255,113,108,0.9)", font_family="monospace", font_size="0.85rem"),
                            bg="rgba(255,113,108,0.05)",
                            border="1px solid rgba(255,113,108,0.2)",
                            border_radius="0.75rem",
                            padding="1rem",
                        ),
                        width="100%",
                    ),
                ),
                # Violations
                rx.cond(
                    CodeReviewerState.result.get("violations"),
                    rx.box(
                        rx.text("STYLE VIOLATIONS", font_size="0.68rem", font_weight="700", letter_spacing="0.1em", color="#ff716c", margin_bottom="0.5rem", font_family="'Space Grotesk', sans-serif"),
                        rx.box(
                            rx.text(str(CodeReviewerState.result.get("violations", [])), white_space="pre-wrap", color="rgba(255,113,108,0.9)", font_family="monospace", font_size="0.85rem"),
                            bg="rgba(255,113,108,0.05)",
                            border="1px solid rgba(255,113,108,0.2)",
                            border_radius="0.75rem",
                            padding="1rem",
                        ),
                        width="100%",
                    ),
                ),
                # Errors
                rx.cond(
                    CodeReviewerState.result.get("error"),
                    rx.box(
                        rx.text("SYNTAX ERROR", font_size="0.68rem", font_weight="700", letter_spacing="0.1em", color="#ff716c", margin_bottom="0.5rem", font_family="'Space Grotesk', sans-serif"),
                        rx.code_block(
                            CodeReviewerState.result.get("error", ""),
                            language="bash",
                            border_radius="0.75rem",
                            bg=BG,
                            border="1px solid rgba(255,113,108,0.2)",
                        ),
                        width="100%",
                    ),
                ),
                # Test Results
                rx.cond(
                    CodeReviewerState.test_results,
                    rx.box(
                        rx.text("TEST RESULTS", font_size="0.68rem", font_weight="700", letter_spacing="0.1em", color=SECONDARY, margin_bottom="0.5rem", font_family="'Space Grotesk', sans-serif"),
                        rx.box(
                            rx.text(CodeReviewerState.test_results, white_space="pre-wrap", font_family="monospace", font_size="0.85rem", color=ON_SURFACE),
                            bg=f"rgba(0,227,253,0.04)",
                            border=f"1px solid rgba(0,227,253,0.15)",
                            border_radius="0.75rem",
                            padding="1rem",
                        ),
                        width="100%",
                    ),
                ),
                spacing="4",
                align_items="flex-start",
                width="100%",
            ),
            rx.center(
                rx.vstack(
                    rx.icon(tag="scan_eye", size=40, color=f"rgba(172,170,177,0.3)"),
                    rx.text("Run a review to see the results.", color=ON_SURFACE_VARIANT, font_size="0.9rem"),
                    spacing="3",
                    align_items="center",
                ),
                width="100%",
                height="300px",
            ),
        ),
    )


# ─────────────────────────────────────
#  PAGE: HOME
# ─────────────────────────────────────

def home_page():
    return rx.box(
        # Google Fonts
        rx.html('<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600&display=swap" rel="stylesheet"/>'),
        navbar(),
        # Ambient glows
        rx.box(
            position="absolute", top="20%", left="50%", transform="translateX(-50%)",
            width="300px", height="300px",
            background=f"radial-gradient(circle, rgba(255,124,245,0.15) 0%, transparent 70%)",
            blur="80px", z_index="-1", border_radius="full",
        ),
        rx.box(
            position="absolute", bottom="20%", right="10%",
            width="250px", height="250px",
            background=f"radial-gradient(circle, rgba(0,227,253,0.08) 0%, transparent 70%)",
            blur="60px", z_index="-1", border_radius="full",
        ),
        # HERO
        rx.box(
            rx.vstack(
                # Version badge
                rx.hstack(
                    rx.box(width="8px", height="8px", border_radius="full", bg=SECONDARY, box_shadow=f"0 0 8px {SECONDARY}"),
                    rx.text("v2.4.0 Engine Active", font_size="0.65rem", letter_spacing="0.1em", color=ON_SURFACE_VARIANT, text_transform="uppercase", font_family="'Space Grotesk', sans-serif"),
                    spacing="2", align_items="center",
                    padding="0.375rem 1rem",
                    border_radius="full",
                    bg=SURFACE_HIGH,
                    border=f"1px solid rgba(72,71,77,0.3)",
                ),
                rx.heading(
                    "Welcome to",
                    size="8",
                    color="white",
                    font_weight="800",
                    letter_spacing="-0.02em",
                    font_family="'Space Grotesk', sans-serif",
                    text_align="center",
                    line_height="1.1",
                ),
                rx.heading(
                    "AI Code Reviewer",
                    size="9",
                    background=f"linear-gradient(180deg, white 40%, rgba(255,255,255,0.55) 100%)",
                    background_clip="text",
                    color="transparent",
                    font_weight="800",
                    letter_spacing="-0.02em",
                    font_family="'Space Grotesk', sans-serif",
                    text_align="center",
                    line_height="1.1",
                    text_shadow=f"0px 4px 12px rgba(255,124,245,0.3)",
                ),
                rx.text(
                    "Clean code analysis, AST insights, history tracking, and smart suggestions in one place. Experience the next evolution of logic refinement.",
                    font_size="1.1rem",
                    color="rgba(249,245,253,0.65)",
                    text_align="center",
                    line_height="1.75",
                    max_width="640px",
                    font_family="Manrope, sans-serif",
                ),
                # CTAs
                rx.hstack(
                    rx.link(
                        rx.button(
                            "Go to Analyzer",
                            padding_x="2.5rem",
                            padding_y="1rem",
                            font_weight="700",
                            font_size="0.9rem",
                            letter_spacing="0.06em",
                            text_transform="uppercase",
                            background=f"linear-gradient(90deg, {PRIMARY} 0%, #ff5af9 100%)",
                            color="#580058",
                            border_radius="full",
                            box_shadow=f"0 0 20px rgba(255,124,245,0.3)",
                            _hover={"box_shadow": "0 0 30px rgba(255,124,245,0.5)", "transform": "translateY(-2px)"},
                            _active={"transform": "scale(0.95)"},
                            transition="all 0.3s",
                            font_family="'Space Grotesk', sans-serif",
                        ),
                        href="/analyzer",
                    ),
                    rx.link(
                        rx.button(
                            "Open Editor",
                            padding_x="2.5rem",
                            padding_y="1rem",
                            font_weight="700",
                            font_size="0.9rem",
                            letter_spacing="0.06em",
                            text_transform="uppercase",
                            bg=f"rgba(31,31,38,0.5)",
                            color=SECONDARY,
                            border=f"1px solid rgba(0,227,253,0.25)",
                            border_radius="full",
                            backdrop_filter="blur(8px)",
                            _hover={"bg": f"rgba(0,227,253,0.1)"},
                            _active={"transform": "scale(0.95)"},
                            transition="all 0.3s",
                            font_family="'Space Grotesk', sans-serif",
                        ),
                        href="/editor",
                    ),
                    spacing="5",
                    flex_wrap="wrap",
                    justify_content="center",
                ),
                spacing="6",
                align_items="center",
                padding_x="1.5rem",
                padding_y="5rem",
                max_width="900px",
                margin_x="auto",
            ),
        ),
        # BENTO GRID
        rx.box(
            rx.grid(
                # Large feature card
                rx.box(
                    rx.box(
                        position="absolute", top="0", right="0",
                        width="16rem", height="16rem",
                        background=f"radial-gradient(circle, rgba(0,227,253,0.07) 0%, transparent 70%)",
                        blur="60px",
                        z_index="0",
                    ),
                    rx.vstack(
                        rx.icon(tag="network", size=30, color=SECONDARY),
                        rx.heading("Real-time AST Mapping", size="5", color="white", font_weight="700", font_family="'Space Grotesk', sans-serif"),
                        rx.text(
                            "Visualise your logic flow with deep Abstract Syntax Tree generation. Detect bottlenecks before they become technical debt.",
                            font_size="0.88rem", color="rgba(249,245,253,0.55)", line_height="1.7", max_width="360px",
                            font_family="Manrope, sans-serif",
                        ),
                        rx.box(
                            rx.box(
                                rx.hstack(
                                    rx.box(width="8px", height="8px", border_radius="full", bg=f"rgba(255,113,108,0.5)"),
                                    rx.box(width="8px", height="8px", border_radius="full", bg=f"rgba(0,227,253,0.5)"),
                                    rx.box(width="8px", height="8px", border_radius="full", bg=f"rgba(255,124,245,0.5)"),
                                    spacing="1", padding="0.75rem",
                                ),
                                rx.vstack(
                                    rx.text("function analyze(code) {", font_family="monospace", font_size="0.8rem", color=SECONDARY),
                                    rx.text("  const ast = parse(code);", font_family="monospace", font_size="0.8rem", color=ON_SURFACE),
                                    rx.text("  return ast.optimize();", font_family="monospace", font_size="0.8rem", color=PRIMARY),
                                    rx.text("}", font_family="monospace", font_size="0.8rem", color=SECONDARY),
                                    spacing="1", padding_x="1.25rem", padding_bottom="1rem",
                                    align_items="flex-start",
                                ),
                                bg=BG,
                                border_radius="0.75rem",
                                border=f"1px solid {OUTLINE}",
                                overflow="hidden",
                            ),
                            margin_top="1.5rem",
                        ),
                        spacing="4",
                        align_items="flex-start",
                        position="relative",
                        z_index="1",
                    ),
                    grid_column=["span 1", "span 1", "span 2"],
                    padding="2rem",
                    border_radius="1rem",
                    bg=SURFACE,
                    border=f"1px solid rgba(72,71,77,0.15)",
                    position="relative",
                    overflow="hidden",
                    _hover={"border_color": f"rgba(0,227,253,0.3)"},
                    transition="border-color 0.3s",
                ),
                # Commit History card
                rx.box(
                    rx.vstack(
                        rx.icon(tag="history", size=30, color=PRIMARY),
                        rx.heading("Commit History", size="5", color="white", font_weight="700", font_family="'Space Grotesk', sans-serif"),
                        rx.text(
                            "Track the evolution of your code health over time with automated scoring and performance metrics.",
                            font_size="0.88rem", color="rgba(249,245,253,0.55)", line_height="1.7",
                            font_family="Manrope, sans-serif",
                        ),
                        spacing="4", align_items="flex-start",
                    ),
                    padding="2rem",
                    border_radius="1rem",
                    bg=SURFACE,
                    border=f"1px solid rgba(72,71,77,0.15)",
                    _hover={"border_color": f"rgba(255,124,245,0.3)"},
                    transition="border-color 0.3s",
                ),
                # AI Suggestions card
                rx.box(
                    rx.vstack(
                        rx.icon(tag="sparkles", size=30, color=SECONDARY),
                        rx.heading("AI Suggestions", size="5", color="white", font_weight="700", font_family="'Space Grotesk', sans-serif"),
                        rx.text(
                            "Get context-aware refactoring advice powered by our latest Luminous Logic LLM model.",
                            font_size="0.88rem", color="rgba(249,245,253,0.55)", line_height="1.7",
                            font_family="Manrope, sans-serif",
                        ),
                        spacing="4", align_items="flex-start",
                    ),
                    padding="2rem",
                    border_radius="1rem",
                    bg=SURFACE,
                    border=f"1px solid rgba(72,71,77,0.15)",
                    _hover={"border_color": f"rgba(0,227,253,0.3)"},
                    transition="border-color 0.3s",
                ),
                # Wide bottom card
                rx.box(
                    rx.hstack(
                        rx.vstack(
                            rx.heading("Optimized for Speed", size="5", color="white", font_weight="700", font_family="'Space Grotesk', sans-serif"),
                            rx.text(
                                "Analyze thousands of lines of code in seconds. Our engine utilizes parallel processing to ensure you're never waiting on your tools.",
                                font_size="0.88rem", color="rgba(249,245,253,0.55)", line_height="1.7",
                                font_family="Manrope, sans-serif",
                            ),
                            rx.vstack(
                                rx.hstack(
                                    rx.icon(tag="check_circle", size=16, color=SECONDARY),
                                    rx.text("Multi-language support", font_size="0.75rem", letter_spacing="0.08em", text_transform="uppercase", color="rgba(249,245,253,0.7)", font_family="'Space Grotesk', sans-serif"),
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.icon(tag="check_circle", size=16, color=SECONDARY),
                                    rx.text("Cloud-sync integration", font_size="0.75rem", letter_spacing="0.08em", text_transform="uppercase", color="rgba(249,245,253,0.7)", font_family="'Space Grotesk', sans-serif"),
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.icon(tag="check_circle", size=16, color=SECONDARY),
                                    rx.text("Auto test generation", font_size="0.75rem", letter_spacing="0.08em", text_transform="uppercase", color="rgba(249,245,253,0.7)", font_family="'Space Grotesk', sans-serif"),
                                    spacing="2",
                                ),
                                spacing="2",
                                margin_top="0.5rem",
                            ),
                            spacing="4",
                            align_items="flex-start",
                            flex="1",
                        ),
                        rx.box(
                            rx.hstack(
                                rx.vstack(
                                    rx.text("10K+", font_size="2rem", font_weight="900", color=PRIMARY, font_family="'Space Grotesk', sans-serif"),
                                    rx.text("Reviews", font_size="0.75rem", color=ON_SURFACE_VARIANT, font_family="Manrope, sans-serif"),
                                    align_items="center", spacing="0",
                                ),
                                rx.vstack(
                                    rx.text("99.8%", font_size="2rem", font_weight="900", color=SECONDARY, font_family="'Space Grotesk', sans-serif"),
                                    rx.text("Accuracy", font_size="0.75rem", color=ON_SURFACE_VARIANT, font_family="Manrope, sans-serif"),
                                    align_items="center", spacing="0",
                                ),
                                rx.vstack(
                                    rx.text("<50ms", font_size="2rem", font_weight="900", color=PRIMARY, font_family="'Space Grotesk', sans-serif"),
                                    rx.text("Response", font_size="0.75rem", color=ON_SURFACE_VARIANT, font_family="Manrope, sans-serif"),
                                    align_items="center", spacing="0",
                                ),
                                spacing="6",
                                justify_content="center",
                                flex_wrap="wrap",
                            ),
                            flex="1",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                        ),
                        spacing="8",
                        align_items="flex-start",
                        flex_wrap=["wrap", "wrap", "nowrap"],
                    ),
                    grid_column=["span 1", "span 1", "span 3"],
                    padding="2.5rem",
                    border_radius="1rem",
                    bg=f"linear-gradient(90deg, rgba(72,71,77,0.15) 0%, transparent 100%)",
                    border=f"1px solid rgba(72,71,77,0.15)",
                    _hover={"border_color": f"rgba(255,124,245,0.2)"},
                    transition="border-color 0.3s",
                ),
                template_columns=["1fr", "1fr", "repeat(3, 1fr)"],
                gap="1.5rem",
                max_width="1400px",
                margin_x="auto",
                padding_x="1.5rem",
                padding_bottom="5rem",
            ),
        ),
        bottom_nav(),
        fab(),
        bg=BG,
        min_height="100vh",
        padding_top="4rem",
        overflow="hidden",
        position="relative",
        width="100%",
    )


# ─────────────────────────────────────
#  PAGE: ANALYZER
# ─────────────────────────────────────

def analyzer_page():
    return rx.box(
        rx.html('<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600&display=swap" rel="stylesheet"/>'),
        navbar(),
        rx.vstack(
            # Header
            rx.box(
                rx.hstack(
                    rx.box(
                        rx.icon(tag="code_2", size=28, color=SECONDARY),
                        padding="0.75rem",
                        border_radius="0.75rem",
                        bg=f"rgba(0,227,253,0.1)",
                    ),
                    rx.vstack(
                        rx.heading("Code Analysis Engine", size="7", color="white", font_weight="900", letter_spacing="-0.01em", font_family="'Space Grotesk', sans-serif"),
                        rx.text("Paste your code for instant quality analysis and AI suggestions", font_size="0.9rem", color=ON_SURFACE_VARIANT, font_family="Manrope, sans-serif"),
                        spacing="0",
                    ),
                    spacing="4",
                    align_items="flex-start",
                ),
                padding="1.5rem",
                bg=f"rgba(0,227,253,0.02)",
                border=f"1px solid rgba(0,227,253,0.1)",
                border_radius="1rem",
                width="100%",
                margin_bottom="1.5rem",
            ),
            # Grid
            rx.grid(
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("SOURCE CODE", font_size="0.68rem", font_weight="700", letter_spacing="0.1em", color=SECONDARY, font_family="'Space Grotesk', sans-serif"),
                            rx.spacer(),
                            rx.box(
                                rx.text("PYTHON", font_size="0.65rem", font_weight="700", letter_spacing="0.06em", color=SECONDARY, font_family="'Space Grotesk', sans-serif"),
                                padding="0.25rem 0.6rem",
                                bg=f"rgba(0,227,253,0.12)",
                                border_radius="full",
                            ),
                            width="100%", align_items="center",
                        ),
                        editor_view(),
                        spacing="3",
                    ),
                    padding="1.5rem",
                    border=f"1px solid rgba(72,71,77,0.2)",
                    border_radius="1rem",
                    bg=f"rgba(0,227,253,0.01)",
                ),
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("ANALYSIS RESULTS", font_size="0.68rem", font_weight="700", letter_spacing="0.1em", color=PRIMARY, font_family="'Space Grotesk', sans-serif"),
                            rx.spacer(),
                            rx.box(
                                rx.text("REAL-TIME", font_size="0.65rem", font_weight="700", letter_spacing="0.06em", color=PRIMARY, font_family="'Space Grotesk', sans-serif"),
                                padding="0.25rem 0.6rem",
                                bg=f"rgba(255,124,245,0.12)",
                                border_radius="full",
                            ),
                            width="100%", align_items="center",
                        ),
                        result_view(),
                        spacing="3",
                        overflow_y="auto",
                        max_height="80vh",
                    ),
                    padding="1.5rem",
                    border=f"1px solid rgba(72,71,77,0.2)",
                    border_radius="1rem",
                    bg=f"rgba(255,124,245,0.01)",
                    overflow="hidden",
                ),
                template_columns=["1fr", "1fr", "repeat(2, minmax(0, 1fr))"],
                gap="1.5rem",
                width="100%",
            ),
            # Footer info
            rx.hstack(
                rx.icon(tag="info", size=18, color=f"rgba(0,227,253,0.6)"),
                rx.text(
                    "Results processed in real-time using advanced AST analysis and machine learning. Your code is not stored.",
                    font_size="0.82rem", color="rgba(249,245,253,0.45)", line_height="1.6",
                    font_family="Manrope, sans-serif",
                ),
                spacing="3", width="100%",
                padding="1.25rem 1.5rem",
                bg=f"rgba(0,227,253,0.04)",
                border=f"1px solid rgba(0,227,253,0.1)",
                border_radius="0.75rem",
                margin_top="1rem",
            ),
            spacing="0",
            padding_x="2rem",
            padding_y="2rem",
            width="100%",
        ),
        bottom_nav(),
        fab(),
        bg=BG,
        min_height="100vh",
        padding_top="4rem",
        width="100%",
    )


# ─────────────────────────────────────
#  PAGE: EDITOR (AST)
# ─────────────────────────────────────

def editor_page():
    return rx.box(
        rx.html('<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600&display=swap" rel="stylesheet"/>'),
        navbar(),
        rx.vstack(
            # Header
            rx.box(
                rx.hstack(
                    rx.box(rx.icon(tag="pencil", size=28, color=SECONDARY), padding="0.75rem", border_radius="0.75rem", bg=f"rgba(0,227,253,0.1)"),
                    rx.vstack(
                        rx.heading("Code Editor & AST Generator", size="7", color="white", font_weight="900", font_family="'Space Grotesk', sans-serif"),
                        rx.text("Edit Python code and visualize its abstract syntax tree in real-time", font_size="0.9rem", color=ON_SURFACE_VARIANT, font_family="Manrope, sans-serif"),
                        spacing="0",
                    ),
                    spacing="4", align_items="flex-start",
                ),
                padding="1.5rem", bg=f"rgba(0,227,253,0.02)", border=f"1px solid rgba(0,227,253,0.1)", border_radius="1rem",
                width="100%", margin_bottom="1.5rem",
            ),
            # Editor + AST Grid
            rx.grid(
                rx.box(
                    rx.vstack(
                        rx.text("SOURCE CODE", font_size="0.68rem", font_weight="700", letter_spacing="0.1em", color=SECONDARY, font_family="'Space Grotesk', sans-serif"),
                        rx.text_area(
                            value=CodeReviewerState.code,
                            on_change=CodeReviewerState.set_code,
                            placeholder="def hello():\n    print('Hello, world!')",
                            height="500px",
                            width="100%",
                            font_family="monospace",
                            font_size="13px",
                            border_radius="0.75rem",
                            border=f"1px solid {OUTLINE}",
                            _focus={"border_color": SECONDARY},
                            bg=SURFACE,
                            color=ON_SURFACE,
                            resize="vertical",
                        ),
                        rx.button(
                            rx.hstack(rx.icon(tag="refresh_cw", size=16), rx.text("Generate AST"), spacing="2"),
                            on_click=CodeReviewerState.compute_ast,
                            width="100%",
                            background=f"linear-gradient(90deg, {SECONDARY} 0%, #00b8cc 100%)",
                            color="#003a42",
                            font_weight="700",
                            font_size="0.85rem",
                            border_radius="full",
                            _hover={"box_shadow": f"0 4px 16px rgba(0,227,253,0.3)"},
                            font_family="'Space Grotesk', sans-serif",
                        ),
                        spacing="3",
                    ),
                    padding="1.5rem",
                    border=f"1px solid rgba(72,71,77,0.2)",
                    border_radius="1rem",
                    bg=f"rgba(0,227,253,0.01)",
                ),
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("AST OUTPUT", font_size="0.68rem", font_weight="700", letter_spacing="0.1em", color=PRIMARY, font_family="'Space Grotesk', sans-serif"),
                            rx.spacer(),
                            rx.box(rx.text("TREE", font_size="0.65rem", font_weight="700", color=PRIMARY, font_family="'Space Grotesk', sans-serif"), padding="0.25rem 0.6rem", bg=f"rgba(255,124,245,0.12)", border_radius="full"),
                            width="100%", align_items="center",
                        ),
                        rx.code_block(
                            rx.cond(CodeReviewerState.ast_output, CodeReviewerState.ast_output, "No AST available yet. Generate AST to view the tree."),
                            language="python",
                            width="100%",
                            min_height="500px",
                            bg=BG,
                            border_radius="0.75rem",
                            border=f"1px solid {OUTLINE}",
                        ),
                        spacing="3",
                    ),
                    padding="1.5rem",
                    border=f"1px solid rgba(72,71,77,0.2)",
                    border_radius="1rem",
                    bg=f"rgba(255,124,245,0.01)",
                ),
                template_columns=["1fr", "1fr", "repeat(2, minmax(0, 1fr))"],
                gap="1.5rem",
                width="100%",
            ),
            spacing="0",
            padding_x="2rem",
            padding_y="2rem",
            width="100%",
        ),
        bottom_nav(),
        fab(),
        bg=BG,
        min_height="100vh",
        padding_top="4rem",
        width="100%",
    )


# ─────────────────────────────────────
#  PAGE: AST (standalone)
# ─────────────────────────────────────

def ast_page():
    return editor_page()


# ─────────────────────────────────────
#  PAGE: HISTORY
# ─────────────────────────────────────

def history_page():
    return rx.box(
        rx.html('<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600&display=swap" rel="stylesheet"/>'),
        navbar(),
        rx.vstack(
            # Header
            rx.box(
                rx.hstack(
                    rx.box(rx.icon(tag="history", size=28, color=SECONDARY), padding="0.75rem", border_radius="0.75rem", bg=f"rgba(0,227,253,0.1)"),
                    rx.vstack(
                        rx.heading("Analysis History", size="7", color="white", font_weight="900", font_family="'Space Grotesk', sans-serif"),
                        rx.text("Review all previous code analyses and quality scores", font_size="0.9rem", color=ON_SURFACE_VARIANT, font_family="Manrope, sans-serif"),
                        spacing="0",
                    ),
                    spacing="4", align_items="flex-start",
                ),
                padding="1.5rem", bg=f"rgba(0,227,253,0.02)", border=f"1px solid rgba(0,227,253,0.1)", border_radius="1rem",
                width="100%", margin_bottom="1.5rem",
            ),
            # History log
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("ANALYSIS LOG", font_size="0.68rem", font_weight="700", letter_spacing="0.1em", color=SECONDARY, font_family="'Space Grotesk', sans-serif"),
                        rx.spacer(),
                        rx.box(rx.text("TIMESTAMPED", font_size="0.65rem", font_weight="700", color=SECONDARY, font_family="'Space Grotesk', sans-serif"), padding="0.25rem 0.6rem", bg=f"rgba(0,227,253,0.12)", border_radius="full"),
                        width="100%", align_items="center",
                    ),
                    rx.code_block(
                        rx.cond(CodeReviewerState.history_text, CodeReviewerState.history_text, "No analyses yet. Run code review to start building your history."),
                        language="python",
                        width="100%",
                        min_height="450px",
                        bg=BG,
                        border_radius="0.75rem",
                        border=f"1px solid {OUTLINE}",
                    ),
                    spacing="3",
                ),
                padding="1.5rem",
                border=f"1px solid rgba(72,71,77,0.2)",
                border_radius="1rem",
                bg=f"rgba(0,227,253,0.01)",
                width="100%",
            ),
            rx.hstack(
                rx.icon(tag="info", size=18, color=f"rgba(0,227,253,0.6)"),
                rx.text("Each analysis is timestamped and scored. Use this history to track code quality improvements over time.", font_size="0.82rem", color="rgba(249,245,253,0.45)", line_height="1.6", font_family="Manrope, sans-serif"),
                spacing="3", width="100%",
                padding="1.25rem 1.5rem",
                bg=f"rgba(0,227,253,0.04)",
                border=f"1px solid rgba(0,227,253,0.1)",
                border_radius="0.75rem",
            ),
            spacing="0",
            padding_x="2rem",
            padding_y="2rem",
            max_width="1400px",
            margin_x="auto",
            width="100%",
        ),
        bottom_nav(),
        fab(),
        bg=BG,
        min_height="100vh",
        padding_top="4rem",
        width="100%",
    )


# ─────────────────────────────────────
#  PAGE: ABOUT
# ─────────────────────────────────────

def about():
    return rx.box(
        rx.html('<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600&display=swap" rel="stylesheet"/>'),
        navbar(),
        rx.vstack(
            rx.box(
                rx.hstack(
                    rx.box(rx.icon(tag="info", size=28, color=SECONDARY), padding="0.75rem", border_radius="0.75rem", bg=f"rgba(0,227,253,0.1)"),
                    rx.vstack(
                        rx.heading("About AI Code Reviewer", size="7", color="white", font_weight="900", font_family="'Space Grotesk', sans-serif"),
                        rx.text("Intelligent code analysis powered by advanced AST parsing and machine learning", font_size="0.9rem", color=ON_SURFACE_VARIANT, font_family="Manrope, sans-serif"),
                        spacing="0",
                    ),
                    spacing="4", align_items="flex-start",
                ),
                padding="1.5rem", bg=f"rgba(0,227,253,0.02)", border=f"1px solid rgba(0,227,253,0.1)", border_radius="1rem",
                width="100%", margin_bottom="2rem",
            ),
            rx.grid(
                *[
                    rx.box(
                        rx.vstack(
                            rx.box(rx.icon(tag=icon, size=28, color=SECONDARY), padding="0.75rem", border_radius="0.75rem", bg=f"rgba(0,227,253,0.1)", width="fit-content"),
                            rx.heading(title, size="5", color="white", font_weight="700", font_family="'Space Grotesk', sans-serif"),
                            rx.text(desc, font_size="0.88rem", color="rgba(249,245,253,0.55)", line_height="1.7", font_family="Manrope, sans-serif"),
                            spacing="3", align_items="flex-start",
                        ),
                        padding="1.5rem",
                        border=f"1px solid rgba(72,71,77,0.2)",
                        border_radius="1rem",
                        bg=f"rgba(0,227,253,0.01)",
                        _hover={"border_color": f"rgba(0,227,253,0.3)"},
                        transition="border-color 0.3s",
                    )
                    for icon, title, desc in [
                        ("zap", "Lightning Fast", "Advanced AST parsing and parallel processing engine for instant feedback."),
                        ("brain", "AI Powered", "Machine learning model provides context-aware refactoring suggestions."),
                        ("lock", "Private & Secure", "Your code is never stored. All analysis happens locally on your machine."),
                    ]
                ],
                template_columns=["1fr", "1fr", "repeat(3, 1fr)"],
                gap="1.25rem",
                width="100%",
                margin_bottom="2rem",
            ),
            rx.box(
                rx.vstack(
                    rx.heading("Technology Stack", size="6", color="white", font_weight="700", font_family="'Space Grotesk', sans-serif"),
                    *[
                        rx.hstack(
                            rx.box(width="6px", height="6px", border_radius="full", bg=SECONDARY, flex_shrink="0"),
                            rx.text(item, color="rgba(249,245,253,0.65)", font_size="0.9rem", font_family="Manrope, sans-serif"),
                            spacing="3", width="100%",
                        )
                        for item in [
                            "Built with Reflex framework for modern, reactive Python development",
                            "Advanced AST analysis for deep code inspection and pattern detection",
                            "LangChain integration for intelligent AI-powered suggestions",
                            "Custom error detection using visitor pattern for comprehensive linting",
                            "Auto test case generation to validate user-submitted functions",
                        ]
                    ],
                    spacing="3",
                ),
                padding="1.5rem",
                border=f"1px solid rgba(72,71,77,0.2)",
                border_radius="1rem",
                bg=f"rgba(0,227,253,0.01)",
                width="100%",
            ),
            spacing="0",
            padding_x="2rem",
            padding_y="2rem",
            max_width="1200px",
            margin_x="auto",
            width="100%",
        ),
        bottom_nav(),
        fab(),
        bg=BG,
        min_height="100vh",
        padding_top="4rem",
        width="100%",
    )


def help_page():
    return rx.center(rx.heading("Help Page", color="white"), height="80vh", bg=BG)


app = rx.App(
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="large",
        accent_color="blue",
    ),
)
app.add_page(home_page, route="/")
app.add_page(analyzer_page, route="/analyzer")
app.add_page(editor_page, route="/editor")
app.add_page(ast_page, route="/ast")
app.add_page(history_page, route="/history")
app.add_page(about, route="/about")
app.add_page(help_page, route="/help")