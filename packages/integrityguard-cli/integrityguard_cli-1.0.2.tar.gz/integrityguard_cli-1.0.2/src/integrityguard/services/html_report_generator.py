from os import path, getcwd
from jinja2 import Environment, FileSystemLoader
from logging import info

class HTMLReportGenerator:
    def __init__(self, template_dir: str = "src/integrityguard/templates", template_name: str = "report.html"):
        if not path.isabs(template_dir):
            template_dir = path.join(getcwd(), template_dir)
            
        self._env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
        self._template_name = template_name

    def generate(self, data: dict, output_path: str = "integrity_guard_report.html"):
        """
        Generates an HTML report from the provided data.
        
        Args:
            data (dict): The report data containing 'summary' and 'findings'.
            output_path (str): The path where the HTML file will be saved.
        """
        try:
            template = self._env.get_template(self._template_name)
            html_content = template.render(
                summary=data["summary"],
                findings=data["findings"]
            )

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            info(f"[+] HTML Report generated successfully at: {output_path}")
            
        except Exception as e:
            info(f"[-] Failed to generate HTML report: {e}")
            raise e
