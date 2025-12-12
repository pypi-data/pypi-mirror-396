import io
import sys

from bedrock_ge.plot import hello_plt


def test_hello_plt():
    # Redirect stdout to capture print output
    captured_output = io.StringIO()
    sys.stdout = captured_output

    # Call the function
    hello_plt()

    # Reset stdout
    sys.stdout = sys.__stdout__

    # Check that the correct message was printed
    expected_message = "Hi Bedrock engineer! bedrock_ge.plot is a placeholder module for Geotechnical Engineering plots.\n"
    assert captured_output.getvalue() == expected_message
