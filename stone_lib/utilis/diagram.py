import io
import os
import subprocess
from typing import Union

from .utilis import temp_dir_with_specific_path


class FlameGraph:
    def __init__(self):
        """A class to generate flame graph."""
        self._temp_dir = temp_dir_with_specific_path("flame_graph")
        self._script_file = os.path.join(self._temp_dir, "flamegraph.pl")

    def _download(self):
        """Download flamegraph.pl from the internet."""
        import urllib.request

        print(f"Downloading flamegraph.pl to: {self._script_file}")
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/brendangregg/FlameGraph/master/flamegraph.pl",
            self._script_file,
        )

    def generate_flame_graph(self, flamegraph_lines: Union[str, io.StringIO]):
        """Generate a flame graph from the input flamegraph lines.

        Args:
            flamegraph_lines (str): flamegraph lines

        Returns:
            str: flame graph

        """
        flamegraph_script = self._script_file
        if not os.path.isfile(flamegraph_script):
            self._download()
        args = ["perl", flamegraph_script, "--countname", "bytes", "--flamechart", "-i"]
        p = subprocess.Popen(
            args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding="utf-8"
        )
        assert p.stdin is not None
        assert p.stdout is not None
        p.stdin.write(flamegraph_lines)
        p.stdin.close()
        result = p.stdout.read()
        p.stdout.close()
        p.wait()
        assert p.wait() == 0
        return result

    def generate_flame_graph_from_file(self, file_path: str):
        """Generate a flame graph from the input file.

        Args:
            file_path (str): the file path

        Returns:
            str: flame graph

        """
        with open(file_path, "r") as file:
            flame_lines = file.read()
        return self.generate_flame_graph(flame_lines)
