import asyncio
import sys
import os
import random
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from playwright.async_api import async_playwright

from jsmon.core.probing import (
    stealth_probe_endpoint, stealth_probe_endpoint_with_auth,
    generate_probe_endpoints, ProbeResultWithScreenshot
)
from jsmon.reporting.html_generator import generate_html_report_with_screenshots
from jsmon.reporting.archive import create_and_upload_archive
from jsmon.network.headers import REALISTIC_USER_AGENTS

async def send_notify_alert_async(message: str, config_path: str = None):
    """Sends a notification using the 'notify' command-line tool."""
    command = ['notify', '-bulk']
    if config_path: command.extend(['-pc', config_path])
    try:
        proc = await asyncio.create_subprocess_exec(
            *command, 
            stdin=asyncio.subprocess.PIPE, 
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate(input=message.encode())
        if proc.returncode == 0: 
            print("[+] Notification sent successfully via notify.")
        else: 
            print(f"[!] Error sending notification via notify: {stderr.decode().strip()}", file=sys.stderr)
    except Exception as e: 
        print(f"[!] An exception occurred while sending notification: {e}", file=sys.stderr)

def format_full_alert(llm_analysis, signal, source_page, js_file_url=None, diff_stats=None):
    """Formats an alert message from AI analysis results with enriched context."""
    alert_message = llm_analysis.get("alert_message", "Suspicious activity detected")
    feature_name = llm_analysis.get("feature_name", "Unknown Feature")
    change_desc = llm_analysis.get("change_description", "No description")
    confidence_score = llm_analysis.get("confidence_score", 0.5)
    
    location = llm_analysis.get("location_inference", {})
    tech_clues = llm_analysis.get("technical_clues", {})
    test_suggestion = llm_analysis.get("test_suggestion", "N/A")
    
    # Confidence emoji
    conf_emoji = "🎯" if confidence_score >= 0.9 else "✅" if confidence_score >= 0.7 else "⚠️"
    
    full_alert = f"{conf_emoji} {alert_message}\n\n"
    full_alert += f"**Feature:** {feature_name}\n"
    full_alert += f"**Change:** {change_desc}\n"
    full_alert += f"**Confidence:** {confidence_score:.0%}\n\n"
    
    # JS File information
    if js_file_url:
        full_alert += f"📄 **JS File:** {js_file_url}\n"
    full_alert += f"🌐 **Source Page:** {source_page}\n"
    
    # Diff stats if available
    if diff_stats:
        lines_added = diff_stats.get('lines_added', 0)
        lines_removed = diff_stats.get('lines_removed', 0)
        full_alert += f"📝 **Changes:** +{lines_added} lines, -{lines_removed} lines\n"
    
    # Technical clues
    if tech_clues:
        full_alert += f"\n🛠️ **Technical Details:**\n"
        
        endpoints = tech_clues.get('endpoints', [])
        if endpoints:
            http_method = tech_clues.get('http_method', 'GET')
            full_alert += f"  • **Endpoints ({http_method}):** {', '.join(endpoints[:3])}\n"
        
        params = tech_clues.get('required_params', [])
        if params:
            full_alert += f"  • **Parameters:** {', '.join(params[:5])}\n"
        
        identifiers = tech_clues.get('code_identifiers', [])
        if identifiers:
            full_alert += f"  • **Code Refs:** {', '.join(identifiers[:3])}\n"
    
    # Location inference
    confidence = location.get('confidence', 'UNKNOWN')
    confidence_emoji_map = {
        'HIGH': '✅', 'MEDIUM': '🔶',
        'LOW': '⚠️', 'NONE': '❓'
    }
    loc_emoji = confidence_emoji_map.get(confidence, '❓')
    
    full_alert += f"\n🔍 **Location Inference** {loc_emoji} {confidence}\n"
    
    if location.get('best_guess_url'):
        full_alert += f"  • **URL:** {location['best_guess_url']}\n"
    if location.get('likely_area') and location['likely_area'] != 'Unknown':
        full_alert += f"  • **Area:** {location['likely_area']}\n"
    if location.get('reasoning'):
        full_alert += f"  • **Why:** {location['reasoning']}\n"
    
    # Test suggestion
    full_alert += f"\n🎯 **How to Test:**\n```bash\n{test_suggestion}\n```\n"
    
    # Metadata footer
    full_alert += f"\n---\n_Rule: {signal.get('rule_id', 'unknown')}_"

    return full_alert

async def generate_report_and_notify(findings_dict, api_keys_dict, args, session, timing, header_manager, session_manager=None):
    """Generates the final report and sends notifications."""
    relevant_hosts = set(findings_dict.keys()) | set(api_keys_dict.keys())
    
    if not relevant_hosts:
        print("[+] No new endpoints or API keys found in this scan cycle.")
        return
    
    # Create a directory for the report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_dir = Path(f"report_{timestamp}")
    screenshots_dir = report_dir / "screenshots"
    report_dir.mkdir(exist_ok=True)
    screenshots_dir.mkdir(exist_ok=True)
    
    probe_semaphore = asyncio.Semaphore(args.threads * 2)
    total_new_endpoints = 0
    total_new_keys = 0
    report_lines = []  # For text version
    all_probe_results = []  # For HTML version
    
    print("[+] Generating final report with probing and screenshots...")
    
    for host in sorted(list(relevant_hosts)):
        report_lines.append("----------------------------------------")
        report_lines.append(f"Host: {host}")

        # API keys section
        host_keys = api_keys_dict.get(host, [])
        if host_keys:
            total_new_keys += len(host_keys)
            report_lines.append("\n🔥 Found Potential API Keys:")
            for key_type, key_value, source in sorted(list(set(host_keys))):
                report_lines.append(f"  - Type: {key_type} | Key: {key_value} | In: {source}")
        
        # Endpoints section
        endpoints = findings_dict.get(host, [])
        if not endpoints:
            continue
        
        report_lines.append("\n📡 Probing New Endpoints:")
        base_url = f"https://{host}"
        
        # Baseline probe
        print(f"[PROBE] Performing baseline probe for {host}...")
        try:
            baseline_result = await stealth_probe_endpoint(
                session, base_url, "/", probe_semaphore, timing, header_manager
            )
            # Convert to ProbeResultWithScreenshot format
            baseline_probe = ProbeResultWithScreenshot(
                url=f"{base_url}/",
                display_name="BASELINE: /",
                status=baseline_result[1],
                title=baseline_result[3],
                content_length=baseline_result[2],
                response_time=0,
                screenshot_path=""
            )
            report_lines.append(f"  {baseline_probe.display_name} - {baseline_probe.title} - "
                              f"{baseline_probe.status} - {baseline_probe.content_length}")
            
            if baseline_probe.status == 0:
                print(f"[!] Baseline probe failed for {host}, skipping.")
                continue
                
        except Exception as e:
            print(f"[!] Baseline probe crashed for {host}: {e}")
            continue

        # Check session
        domain_session = None
        if session_manager and getattr(args, 'enable_auth_mode', False):
            domain_session = await session_manager.get_session(host)

        playwright_instance = None
        browser = None
        context = None

        try:
            print(f"[BROWSER PROBE] Initializing shared browser for {host}")
            try:
                playwright_instance = await asyncio.wait_for(async_playwright().start(), timeout=30.0)
                browser = await asyncio.wait_for(playwright_instance.chromium.launch(
                    headless=True,
                    args=['--disable-dev-shm-usage', '--no-sandbox']
                ), timeout=30.0)
                context = await asyncio.wait_for(browser.new_context(
                    user_agent=random.choice(REALISTIC_USER_AGENTS),
                    viewport={'width': 1366, 'height': 768}
                ), timeout=15.0)
            except asyncio.TimeoutError:
                print(f"[!!!] CRITICAL: Browser initialization timed out for {host}. Skipping host.", file=sys.stderr)
                continue 

            if domain_session:
                await context.add_cookies(domain_session.cookies)
                print(f"[BROWSER PROBE] Session cookies injected for {host}")
            else:
                print(f"[BROWSER PROBE] No session - browser will work in public mode")

            unique_endpoints = sorted(list(set(endpoints)))
            total_new_endpoints += len(unique_endpoints)
            
            all_probe_tasks = []
            for ep in unique_endpoints:
                probe_variants = generate_probe_endpoints(ep, max_variants=2)
                for probe_info in probe_variants:
                    task = asyncio.create_task(
                        stealth_probe_endpoint_with_auth(
                            session, base_url, probe_info, probe_semaphore, 
                            timing, header_manager, domain_session,
                            playwright_context=context,
                            screenshots_dir=screenshots_dir
                        )
                    )
                    all_probe_tasks.append(task)
            
            if not all_probe_tasks:
                continue

            print(f"\n[🔍] Probing {len(all_probe_tasks)} endpoints for {host}...")
            pbar_probe = tqdm(
                total=len(all_probe_tasks), 
                desc=f"Probing {host}", 
                unit="endpoint",
                position=0,
                leave=True
            )
            
            results = []
            for task in asyncio.as_completed(all_probe_tasks):
                try:
                    result = await asyncio.wait_for(task, timeout=90)
                    results.append(result)
                    pbar_probe.update(1)
                except asyncio.TimeoutError:
                    print(f"\n[⚠️] Probe timeout, skipping endpoint")
                    pbar_probe.update(1)
                    results.append(ProbeResultWithScreenshot(
                        url="Unknown", display_name="Timeout", status=0,
                        title="Probe Timeout (90s)", content_length=0,
                        response_time=0, screenshot_path="", fetch_method="timeout"
                    ))
                except Exception as e:
                    pbar_probe.update(1)
                    results.append(ProbeResultWithScreenshot(
                        url="Unknown", display_name="Error", status=0,
                        title=f"Error: {type(e).__name__}", content_length=0,
                        response_time=0, screenshot_path=""
                    ))
            
            pbar_probe.close()
            
            # Live display of probing results
            probe_summary = {'200': 0, '3xx': 0, '4xx': 0, '5xx': 0, 'errors': 0}
            
            for result in results:
                if isinstance(result, Exception):
                    probe_summary['errors'] += 1
                else:
                    if result.status == 200: probe_summary['200'] += 1
                    elif 300 <= result.status < 400: probe_summary['3xx'] += 1
                    elif 400 <= result.status < 500: probe_summary['4xx'] += 1
                    elif result.status >= 500: probe_summary['5xx'] += 1
                    
                    all_probe_results.append(result)
                    report_lines.append(f"  {result.display_name} - {result.title} - "
                                      f"{result.status} - {result.content_length}")
            
            print(f"\n[📊] {host} probe results:")
            print(f"    ✅ 200 OK: {probe_summary['200']}")
            print(f"    🔀 3xx: {probe_summary['3xx']}")
            print(f"    ❌ 4xx: {probe_summary['4xx']}")
            print(f"    💥 5xx: {probe_summary['5xx']}")
            print(f"    ⚠️ Errors: {probe_summary['errors']}")

        finally:
            print(f"[BROWSER PROBE] Cleaning up browser instance for {host}...")
            try:
                if context: await asyncio.wait_for(context.close(), timeout=10.0)
                if browser: await asyncio.wait_for(browser.close(), timeout=10.0)
                if playwright_instance: await asyncio.wait_for(playwright_instance.stop(), timeout=10.0)
                print(f"[BROWSER PROBE] Cleanup successful for {host}.")
            except Exception as e:
                print(f"[!!!] CRITICAL: Browser cleanup failed for {host}: {e}", file=sys.stderr)

    if not report_lines and not all_probe_results:
        return
    
    report_lines.append("----------------------------------------")
    text_report_content = "\n".join(report_lines)
    
    # Save text report
    text_report_path = report_dir / "report.txt"
    with open(text_report_path, 'w', encoding='utf-8') as f:
        f.write(text_report_content)
    
    # Generate HTML report with screenshots
    html_report_path = generate_html_report_with_screenshots(
        all_probe_results, api_keys_dict, report_dir
    )
    
    # Create and upload archive
    download_link = await create_and_upload_archive(report_dir, timestamp)
    
    # Prepare notification message
    header_parts = []
    if total_new_endpoints > 0:
        header_parts.append(f"{total_new_endpoints} new endpoints")
    if total_new_keys > 0:
        header_parts.append(f"{total_new_keys} potential API keys")

    if not header_parts:
        return

    header = f"🔍 JS-Analyzer found " + " and ".join(header_parts) + "."

    total_probed = len([r for r in all_probe_results if r.status > 0])
    status_200 = sum(1 for r in all_probe_results if r.status == 200)
    status_3xx = sum(1 for r in all_probe_results if 300 <= r.status < 400)
    status_4xx = sum(1 for r in all_probe_results if 400 <= r.status < 500)

    stats_summary = (
        f"\n📊 Probing Summary:\n"
        f"  ✅ 200 OK: {status_200}\n"
        f"  🔀 3xx Redirects: {status_3xx}\n"
        f"  ❌ 4xx Errors: {status_4xx}"
    )

    if download_link:
        message = f"{header}{stats_summary}\n\n📦 Full report: {download_link}"
    else:
        local_path = os.path.abspath(report_dir)
        message = (
            f"{header}{stats_summary}\n\n"
            f"⚠️ Upload failed - report saved locally:\n"
            f"📁 {local_path}\n\n"
            f"💡 You can manually upload using:\n"
            f"   curl -F 'file=@report_{timestamp}.rar' https://store1.gofile.io/uploadFile"
        )
    
    await send_notify_alert_async(message, args.notify_provider_config)
