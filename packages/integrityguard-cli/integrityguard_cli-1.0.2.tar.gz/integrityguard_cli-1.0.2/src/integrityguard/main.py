def main():    
    from argparse import ArgumentParser
    from integrityguard.vulnerabilities.checkers.docker_group_check import DockerGroupCheck
    from integrityguard.vulnerabilities.checkers.docker_soc_poc import DockerSockPoC
    from integrityguard.vulnerabilities.integrity_guard_tool import IntegrityGuardTool

    from logging import basicConfig, INFO

    basicConfig(
        level=INFO,
        format='%(message)s'
    )
    
    parser = ArgumentParser(description="Docker Security Assessment Tool")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--html", action="store_true", help="Create a report in HTML")
    args = parser.parse_args()

    output_formats = [mode for mode, is_enabled in vars(args).items() if is_enabled]

    tool = IntegrityGuardTool([
        DockerGroupCheck(),
        DockerSockPoC()
    ], output_formats)
    
    tool.run_analysis()

if __name__ == "__main__":
    main()