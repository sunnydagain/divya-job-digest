import logging
import smtplib
import ssl
from datetime import date
from email.message import EmailMessage
from html import escape

from .job import Job

log = logging.getLogger(__name__)


CAP = 10  # we only ever show the top N matches; the rest are dropped


def send(
    jobs: list[Job],
    sources_scanned: list[str],
    firms_skipped: int,
    max_score: int,
    gmail_user: str,
    gmail_pw: str,
    recipient: str,
) -> None:
    today = date.today().isoformat()
    n = len(jobs)
    subject = f"Daily job digest — {n} match{'es' if n != 1 else ''} — {today}"

    text_body = _render_text(jobs, sources_scanned, firms_skipped, max_score)
    html_body = _render_html(jobs, sources_scanned, firms_skipped, max_score)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = recipient
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_user, gmail_pw)
        server.send_message(msg)
    log.info("Email sent to %s", recipient)


def _render_text(jobs: list[Job], sources_scanned: list[str], firms_skipped: int, max_score: int) -> str:
    if not jobs:
        return (
            "0 matches today.\n\n"
            f"Sources scanned: {', '.join(sources_scanned)}.\n"
            f"Curated firms skipped (no ATS slug configured): {firms_skipped}.\n"
            "Filters applied: UK location, mid-senior seniority, exclusions list.\n\n"
            "If you see this every day for a week, edit config/firms_list.yml to add ATS slugs, "
            "or loosen the seniority filter in config/criteria.yml.\n"
        )

    n = len(jobs)
    if n >= CAP:
        header = f"Top {CAP} matches for {date.today().isoformat()} (more passed; truncated to top {CAP}):"
    else:
        header = f"{n} match{'es' if n != 1 else ''} for {date.today().isoformat()} (cap is {CAP}; this is the full set that passed today's filters):"

    lines = [header + "\n"]
    for i, j in enumerate(jobs, 1):
        summary = ", ".join(j.signals) if j.signals else "weak match"
        salary_line = f"   Salary: {j.salary}\n" if j.salary else ""
        lines.append(
            f"{i}. {j.title} — {j.company or 'Unknown firm'}"
            f" ({j.tier or 'untiered'})\n"
            f"   Location: {j.location or 'n/a'} | Posted: {j.posted or 'n/a'} | Score: {j.score} / {max_score}\n"
            f"{salary_line}"
            f"   Fit: {summary}\n"
            f"   Link: {j.url}\n"
            f"   Source: {j.source}\n"
        )
    lines.append("\nSponsor status: verify manually on gov.uk before applying.")
    return "\n".join(lines)


def _render_html(jobs: list[Job], sources_scanned: list[str], firms_skipped: int, max_score: int) -> str:
    if not jobs:
        return f"""<html><body style="font-family:system-ui,sans-serif;max-width:640px;margin:auto;">
<h2>0 matches today</h2>
<p>Sources scanned: {escape(', '.join(sources_scanned))}.</p>
<p>Curated firms skipped (no ATS slug configured): {firms_skipped}.</p>
<p>Filters applied: UK location, mid-senior seniority, exclusions list.</p>
<p style="color:#666;font-size:0.9em;">If you see this every day for a week, edit
<code>config/firms_list.yml</code> to add ATS slugs, or loosen
<code>config/criteria.yml</code>.</p>
</body></html>"""

    items = []
    for i, j in enumerate(jobs, 1):
        summary = ", ".join(j.signals) if j.signals else "weak match"
        salary_html = (
            f'<div style="color:#1a7f37;font-size:0.9em;font-weight:500;">Salary: {escape(j.salary)}</div>'
            if j.salary else ""
        )
        items.append(f"""
<li style="margin-bottom:1.25em;">
  <a href="{escape(j.url)}" style="font-size:1.05em;font-weight:600;">{escape(j.title)}</a>
  <div>{escape(j.company or 'Unknown firm')} — <em>{escape(j.tier or 'untiered')}</em></div>
  <div style="color:#555;font-size:0.9em;">
    {escape(j.location or 'n/a')} · Posted {escape(j.posted or 'n/a')} · Score <b>{j.score} / {max_score}</b>
  </div>
  {salary_html}
  <div style="color:#333;font-size:0.9em;">Fit: {escape(summary)}</div>
  <div style="color:#888;font-size:0.8em;">Source: {escape(j.source)}</div>
</li>""")

    n = len(jobs)
    if n >= CAP:
        subtitle = f"Top {CAP} of more candidates that passed today's filters."
    else:
        subtitle = f"All {n} match{'es' if n != 1 else ''} that passed today's filters (cap is {CAP})."

    return f"""<html><body style="font-family:system-ui,sans-serif;max-width:640px;margin:auto;">
<h2 style="margin-bottom:0.1em;">{n} match{'es' if n != 1 else ''} — {date.today().isoformat()}</h2>
<div style="color:#666;font-size:0.9em;margin-bottom:1em;">{escape(subtitle)}</div>
<ol>{''.join(items)}</ol>
<p style="color:#666;font-size:0.85em;border-top:1px solid #eee;padding-top:0.75em;">
Sponsor status: verify manually on
<a href="https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers">gov.uk</a>
before applying.
</p>
</body></html>"""
