import subprocess
import sys
import signal


def run_dbt(args: list[str], stream_output: bool = False) -> tuple[int, list[str]]:
    """
    Run a dbt command and capture its output.

    Args:
        args (list[str]): The command and arguments to execute, e.g. ["dbt", "build", "-s", "model"].
        stream_output (bool, optional): When True, write dbt's stdout to this process' stdout as it arrives. Defaults to False.
    Returns:
        tuple[int, list[str]]: The process return code and a list of stdout lines.
    """
    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,  # line-buffered
        preexec_fn=None if sys.platform == "win32" else lambda: signal.signal(signal.SIGINT, signal.SIG_IGN),
    )

    try:
        output_lines: list[str] = []
        # Stream output line by line
        assert process.stdout is not None  # for type checkers
        for line in process.stdout:
            output_lines.append(line)
            if stream_output:
                # Write through to stdout without adding extra newlines
                sys.stdout.write(line)
                sys.stdout.flush()

        returncode = process.wait()

        if returncode != 0:
            raise subprocess.CalledProcessError(returncode, args, output="".join(output_lines))

        return returncode, output_lines

    except KeyboardInterrupt:
        sys.stderr.write("\nKeyboardInterrupt received, terminating dbt...\n")
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            sys.stderr.write("dbt did not exit gracefully, killing...\n")
            process.kill()
        sys.exit(130)

    except Exception as e:
        sys.stderr.write(f"An error occurred while running dbt: {e}\n")
        process.kill()
        sys.exit(1)
