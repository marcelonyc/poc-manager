"""Chart generation utilities for POC reports.

Generates matplotlib charts as PNG images (for PDF embedding)
and base64-encoded data URIs (for Markdown embedding).
"""

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for server-side rendering

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from io import BytesIO
import base64
import tempfile
import os
from typing import Dict, List, Optional, Tuple
from datetime import date, datetime


# Consistent color palette
STATUS_COLORS = {
    "not_started": "#9CA3AF",  # gray
    "in_progress": "#3B82F6",  # blue
    "completed": "#10B981",  # green
    "blocked": "#EF4444",  # red
    "satisfied": "#10B981",  # green
    "partially_satisfied": "#F59E0B",  # amber
    "not_satisfied": "#EF4444",  # red
}

STATUS_LABELS = {
    "not_started": "Not Started",
    "in_progress": "In Progress",
    "completed": "Completed",
    "blocked": "Blocked",
    "satisfied": "Satisfied",
    "partially_satisfied": "Partially Satisfied",
    "not_satisfied": "Not Satisfied",
}


def _apply_theme(fig, ax, primary_color: str = "#0066cc"):
    """Apply consistent styling to charts."""
    fig.patch.set_facecolor("#FFFFFF")
    if ax is not None:
        ax.set_facecolor("#FAFAFA")
        for spine in ax.spines.values():
            spine.set_color("#E5E7EB")
            spine.set_linewidth(0.5)


def _save_chart(fig, as_base64: bool = False, dpi: int = 150) -> str:
    """Save chart to a temp file path or return base64 data URI.

    Args:
        fig: matplotlib figure
        as_base64: If True, return base64 data URI; if False, return temp file path
        dpi: Resolution

    Returns:
        File path string or base64 data URI string
    """
    if as_base64:
        buf = BytesIO()
        fig.savefig(
            buf,
            format="png",
            dpi=dpi,
            bbox_inches="tight",
            facecolor=fig.get_facecolor(),
            edgecolor="none",
        )
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        return f"data:image/png;base64,{encoded}"
    else:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        fig.savefig(
            tmp.name,
            format="png",
            dpi=dpi,
            bbox_inches="tight",
            facecolor=fig.get_facecolor(),
            edgecolor="none",
        )
        plt.close(fig)
        return tmp.name


def generate_task_status_pie_chart(
    status_counts: Dict[str, int],
    primary_color: str = "#0066cc",
    as_base64: bool = False,
) -> Optional[str]:
    """Generate a donut/pie chart showing task status distribution.

    Args:
        status_counts: Dict mapping status string to count, e.g. {"completed": 5, "in_progress": 3}
        primary_color: Tenant primary color for theming
        as_base64: Return base64 data URI if True, else temp file path

    Returns:
        File path or base64 string, or None if no data
    """
    # Filter out zero counts
    filtered = {k: v for k, v in status_counts.items() if v > 0}
    if not filtered:
        return None

    labels = [
        STATUS_LABELS.get(k, k.replace("_", " ").title()) for k in filtered
    ]
    sizes = list(filtered.values())
    chart_colors = [STATUS_COLORS.get(k, "#9CA3AF") for k in filtered]
    total = sum(sizes)

    fig, ax = plt.subplots(1, 1, figsize=(5, 4))
    _apply_theme(fig, None, primary_color)
    fig.patch.set_facecolor("#FFFFFF")

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,
        colors=chart_colors,
        autopct=lambda pct: f"{int(round(pct / 100.0 * total))}",
        startangle=90,
        pctdistance=0.75,
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2),
    )

    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_fontweight("bold")
        autotext.set_color("white")

    # Center text
    ax.text(
        0,
        0,
        f"{total}",
        ha="center",
        va="center",
        fontsize=28,
        fontweight="bold",
        color=primary_color,
    )
    ax.text(
        0,
        -0.15,
        "Total Tasks",
        ha="center",
        va="center",
        fontsize=10,
        color="#6B7280",
    )

    # Legend
    legend = ax.legend(
        wedges,
        [f"{l} ({s})" for l, s in zip(labels, sizes)],
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=9,
        frameon=False,
    )

    ax.set_title(
        "Task Status Distribution",
        fontsize=13,
        fontweight="bold",
        color="#1F2937",
        pad=15,
    )

    return _save_chart(fig, as_base64)


def generate_success_criteria_chart(
    criteria_data: List[Dict],
    primary_color: str = "#0066cc",
    as_base64: bool = False,
) -> Optional[str]:
    """Generate horizontal bar chart for success criteria achievement.

    Args:
        criteria_data: List of dicts with keys: title, target_value, achieved_value, is_met, importance_level
        primary_color: Tenant primary color
        as_base64: Return base64 if True

    Returns:
        File path or base64 string, or None if no data
    """
    if not criteria_data:
        return None

    # Try to extract numeric values for comparison
    numeric_criteria = []
    for c in criteria_data:
        try:
            target = float(
                str(c.get("target_value", "0"))
                .replace("%", "")
                .replace(",", "")
                .strip()
            )
            achieved = float(
                str(c.get("achieved_value", "0"))
                .replace("%", "")
                .replace(",", "")
                .strip()
            )
            numeric_criteria.append(
                {
                    "title": c["title"][:35]
                    + ("..." if len(c["title"]) > 35 else ""),
                    "target": target,
                    "achieved": achieved,
                    "is_met": c.get("is_met", False),
                    "importance": c.get("importance_level", 3),
                }
            )
        except (ValueError, TypeError):
            # Non-numeric criteria — show as met/not-met only
            numeric_criteria.append(
                {
                    "title": c["title"][:35]
                    + ("..." if len(c["title"]) > 35 else ""),
                    "target": 100,
                    "achieved": 100 if c.get("is_met") else 0,
                    "is_met": c.get("is_met", False),
                    "importance": c.get("importance_level", 3),
                }
            )

    if not numeric_criteria:
        return None

    n = len(numeric_criteria)
    fig_height = max(3, n * 0.8 + 1.5)
    fig, ax = plt.subplots(1, 1, figsize=(7, fig_height))
    _apply_theme(fig, ax, primary_color)

    titles = [c["title"] for c in reversed(numeric_criteria)]
    targets = [c["target"] for c in reversed(numeric_criteria)]
    achieved = [c["achieved"] for c in reversed(numeric_criteria)]
    met_status = [c["is_met"] for c in reversed(numeric_criteria)]
    importance = [c["importance"] for c in reversed(numeric_criteria)]

    y_pos = np.arange(n)
    bar_height = 0.35

    bars_target = ax.barh(
        y_pos + bar_height / 2,
        targets,
        bar_height,
        label="Target",
        color="#E5E7EB",
        edgecolor="#D1D5DB",
    )
    bars_achieved = ax.barh(
        y_pos - bar_height / 2,
        achieved,
        bar_height,
        label="Achieved",
        color=[("#10B981" if m else "#F59E0B") for m in met_status],
        edgecolor="white",
    )

    # Add importance stars
    for i, imp in enumerate(importance):
        stars = "★" * imp + "☆" * (5 - imp)
        ax.text(
            -0.02,
            i,
            stars,
            ha="right",
            va="center",
            fontsize=6,
            color="#F59E0B",
            transform=ax.get_yaxis_transform(),
        )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(titles, fontsize=9)
    ax.set_xlabel("Value", fontsize=10, color="#6B7280")
    ax.set_title(
        "Success Criteria Achievement",
        fontsize=13,
        fontweight="bold",
        color="#1F2937",
        pad=15,
    )
    ax.legend(loc="lower right", fontsize=9, frameon=True, facecolor="white")
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    plt.tight_layout()
    return _save_chart(fig, as_base64)


def generate_progress_gauge(
    completion_pct: float,
    success_score: Optional[int] = None,
    primary_color: str = "#0066cc",
    as_base64: bool = False,
) -> Optional[str]:
    """Generate a semi-circular gauge showing overall POC progress.

    Args:
        completion_pct: Percentage of tasks completed (0-100)
        success_score: Overall success score (0-100), optional
        primary_color: Tenant primary color
        as_base64: Return base64 if True

    Returns:
        File path or base64 string
    """
    fig, axes = plt.subplots(
        1,
        2 if success_score is not None else 1,
        figsize=(8 if success_score is not None else 4, 3.5),
    )
    fig.patch.set_facecolor("#FFFFFF")

    if success_score is not None:
        ax_list = axes
    else:
        ax_list = [axes]

    def draw_gauge(ax, value, label, color):
        # Background arc
        theta = np.linspace(np.pi, 0, 100)
        ax.plot(
            np.cos(theta),
            np.sin(theta),
            color="#E5E7EB",
            linewidth=18,
            solid_capstyle="round",
        )

        # Value arc
        filled = int(value)
        if filled > 0:
            theta_filled = np.linspace(
                np.pi, np.pi - (np.pi * min(filled, 100) / 100), max(filled, 1)
            )
            # Color gradient based on value
            if filled >= 75:
                arc_color = "#10B981"
            elif filled >= 50:
                arc_color = "#F59E0B"
            elif filled >= 25:
                arc_color = "#F97316"
            else:
                arc_color = "#EF4444"
            ax.plot(
                np.cos(theta_filled),
                np.sin(theta_filled),
                color=arc_color,
                linewidth=18,
                solid_capstyle="round",
            )

        # Center value
        ax.text(
            0,
            0.15,
            f"{int(value)}%",
            ha="center",
            va="center",
            fontsize=28,
            fontweight="bold",
            color="#1F2937",
        )
        ax.text(
            0,
            -0.15,
            label,
            ha="center",
            va="center",
            fontsize=11,
            color="#6B7280",
        )

        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-0.5, 1.3)
        ax.set_aspect("equal")
        ax.axis("off")

    draw_gauge(ax_list[0], completion_pct, "Task Completion", primary_color)
    if success_score is not None and len(ax_list) > 1:
        draw_gauge(ax_list[1], success_score, "Success Score", primary_color)

    plt.tight_layout()
    return _save_chart(fig, as_base64)


def generate_timeline_chart(
    tasks: List[Dict],
    poc_start: Optional[date] = None,
    poc_end: Optional[date] = None,
    primary_color: str = "#0066cc",
    as_base64: bool = False,
) -> Optional[str]:
    """Generate a Gantt-style timeline chart for tasks.

    Args:
        tasks: List of dicts with keys: title, start_date, due_date, status, is_group
        poc_start: POC start date
        poc_end: POC end date
        primary_color: Tenant primary color
        as_base64: Return base64 if True

    Returns:
        File path or base64 string, or None if no schedulable tasks
    """
    # Filter tasks that have at least one date
    schedulable = [
        t for t in tasks if t.get("start_date") or t.get("due_date")
    ]
    if not schedulable:
        return None

    # Determine date range
    all_dates = []
    if poc_start:
        all_dates.append(poc_start)
    if poc_end:
        all_dates.append(poc_end)
    for t in schedulable:
        if t.get("start_date"):
            all_dates.append(t["start_date"])
        if t.get("due_date"):
            all_dates.append(t["due_date"])

    min_date = min(all_dates)
    max_date = max(all_dates)
    date_range = (max_date - min_date).days or 1

    n = len(schedulable)
    fig_height = max(3, n * 0.5 + 2)
    fig, ax = plt.subplots(1, 1, figsize=(9, fig_height))
    _apply_theme(fig, ax, primary_color)

    for i, task in enumerate(reversed(schedulable)):
        start = task.get("start_date") or task.get("due_date")
        end = task.get("due_date") or task.get("start_date")
        status = task.get("status", "not_started")
        is_group = task.get("is_group", False)

        start_offset = (start - min_date).days
        duration = max((end - start).days, 1)

        color = STATUS_COLORS.get(status, "#9CA3AF")
        alpha = 1.0 if not is_group else 0.7
        height = 0.6 if not is_group else 0.5

        bar = ax.barh(
            i,
            duration,
            left=start_offset,
            height=height,
            color=color,
            alpha=alpha,
            edgecolor="white",
            linewidth=0.5,
        )

        # Task label
        label = task["title"][:30] + ("..." if len(task["title"]) > 30 else "")
        prefix = "📁 " if is_group else ""
        ax.text(
            -0.5,
            i,
            f"{prefix}{label}",
            ha="right",
            va="center",
            fontsize=8,
            color="#374151",
            transform=ax.get_yaxis_transform(),
        )

    # Today line
    today = date.today()
    if min_date <= today <= max_date:
        today_offset = (today - min_date).days
        ax.axvline(
            x=today_offset,
            color="#EF4444",
            linewidth=1.5,
            linestyle="--",
            alpha=0.7,
            label="Today",
        )
        ax.text(
            today_offset,
            n,
            "Today",
            ha="center",
            va="bottom",
            fontsize=8,
            color="#EF4444",
            fontweight="bold",
        )

    # X-axis dates
    num_ticks = min(10, date_range + 1)
    tick_positions = np.linspace(0, date_range, num_ticks)
    from datetime import timedelta

    tick_labels = [
        (min_date + timedelta(days=int(d))).strftime("%b %d")
        for d in tick_positions
    ]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=8, rotation=45, ha="right")

    ax.set_yticks(range(n))
    ax.set_yticklabels([""] * n)  # Labels via text() above
    ax.set_title(
        "POC Timeline", fontsize=13, fontweight="bold", color="#1F2937", pad=15
    )

    # Legend
    legend_patches = [
        mpatches.Patch(color=c, label=STATUS_LABELS.get(s, s))
        for s, c in STATUS_COLORS.items()
        if s in ["not_started", "in_progress", "completed", "blocked"]
    ]
    ax.legend(
        handles=legend_patches,
        loc="upper right",
        fontsize=7,
        frameon=True,
        facecolor="white",
    )

    ax.grid(axis="x", alpha=0.3, linestyle="--")
    plt.tight_layout()
    return _save_chart(fig, as_base64)


def generate_workload_chart(
    assignee_data: Dict[str, Dict[str, int]],
    primary_color: str = "#0066cc",
    as_base64: bool = False,
) -> Optional[str]:
    """Generate stacked bar chart showing workload per team member.

    Args:
        assignee_data: Dict mapping assignee name to status counts,
            e.g. {"John": {"completed": 3, "in_progress": 2, "not_started": 1}}
        primary_color: Tenant primary color
        as_base64: Return base64 if True

    Returns:
        File path or base64 string, or None if no data
    """
    if not assignee_data:
        return None

    names = list(assignee_data.keys())
    statuses = ["completed", "in_progress", "not_started", "blocked"]
    n = len(names)

    fig_height = max(3, n * 0.6 + 1.5)
    fig, ax = plt.subplots(1, 1, figsize=(7, fig_height))
    _apply_theme(fig, ax, primary_color)

    y_pos = np.arange(n)
    left = np.zeros(n)

    for status in statuses:
        values = [assignee_data[name].get(status, 0) for name in names]
        color = STATUS_COLORS.get(status, "#9CA3AF")
        label = STATUS_LABELS.get(status, status)
        ax.barh(
            y_pos,
            values,
            left=left,
            height=0.5,
            color=color,
            label=label,
            edgecolor="white",
            linewidth=0.5,
        )
        left += np.array(values)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(
        [n[:20] + ("..." if len(n) > 20 else "") for n in names], fontsize=9
    )
    ax.set_xlabel("Number of Tasks", fontsize=10, color="#6B7280")
    ax.set_title(
        "Team Workload Distribution",
        fontsize=13,
        fontweight="bold",
        color="#1F2937",
        pad=15,
    )
    ax.legend(loc="lower right", fontsize=8, frameon=True, facecolor="white")
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    # Add total labels
    for i, name in enumerate(names):
        total = sum(assignee_data[name].values())
        ax.text(
            left[i] + 0.2,
            i,
            str(total),
            va="center",
            fontsize=9,
            fontweight="bold",
            color="#6B7280",
        )

    plt.tight_layout()
    return _save_chart(fig, as_base64)


def generate_activity_chart(
    activity_data: List[Dict],
    primary_color: str = "#0066cc",
    as_base64: bool = False,
) -> Optional[str]:
    """Generate bar chart showing comment/activity over time.

    Args:
        activity_data: List of dicts with keys: period (str), count (int)
        primary_color: Tenant primary color
        as_base64: Return base64 if True

    Returns:
        File path or base64 string, or None if no data
    """
    if not activity_data:
        return None

    fig, ax = plt.subplots(1, 1, figsize=(7, 3.5))
    _apply_theme(fig, ax, primary_color)

    periods = [d["period"] for d in activity_data]
    counts = [d["count"] for d in activity_data]

    bars = ax.bar(
        range(len(periods)),
        counts,
        color=primary_color,
        alpha=0.8,
        edgecolor="white",
        linewidth=0.5,
        width=0.7,
    )

    # Value labels on bars
    for bar, count in zip(bars, counts):
        if count > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                str(count),
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                color="#6B7280",
            )

    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels(periods, fontsize=8, rotation=45, ha="right")
    ax.set_ylabel("Comments", fontsize=10, color="#6B7280")
    ax.set_title(
        "Activity Over Time",
        fontsize=13,
        fontweight="bold",
        color="#1F2937",
        pad=15,
    )
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    plt.tight_layout()
    return _save_chart(fig, as_base64)


def cleanup_chart_files(file_paths: List[str]):
    """Remove temporary chart files."""
    for path in file_paths:
        if path and not path.startswith("data:") and os.path.exists(path):
            try:
                os.unlink(path)
            except OSError:
                pass
