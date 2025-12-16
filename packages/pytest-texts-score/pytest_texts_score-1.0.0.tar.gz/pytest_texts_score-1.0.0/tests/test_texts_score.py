from pytest_texts_score.api import texts_expect_f1_equal, texts_expect_f1_range


# Test for identical texts
# Expected behavior: F1 score should be 1.0 when texts are exactly the same
def test_identical():
    """Test F1 score with identical texts - should return perfect score of 1.0"""
    texts_expect_f1_equal("Patrik and Peter are people.",
                          "Patrik and Peter are people.", 1.0)


# Test for texts with differences
# Expected behavior: F1 score should be approximately 2/3
def test_difference():
    """Test F1 score with different texts - expects score around 2/3"""
    texts_expect_f1_equal("Patrik and Peter are workers.",
                          "Patrik is worker.",
                          2 / 3,
                          max_delta=0.3)


# Test for completely unrelated texts
# Expected behavior: F1 score should be 0 when texts share no common information
def test_zero():
    """Test F1 score with completely unrelated texts - should return 0"""
    texts_expect_f1_equal("Patrik is programmer.", "Peter loves sport.", 0)


# Test for partially matching texts with range
# Expected behavior: F1 score should fall within specified range (0.6667)
def test_half_complex_range():
    """Test F1 score range for partially matching texts - expects score between 0.3 and 0.75"""
    texts_expect_f1_range(
        "Patrik and Peter are people.",
        "Patrik is human.",
        min_score=0.3,
        max_score=0.75,
    )


# Test data for long text comparison
long_expected = """REST uses HTTP to send data between systems.
A network connects computers so they can share information.
Object-oriented programming uses objects and classes to organize code.
Data mining finds patterns in large sets of information.
A virtual machine runs software like it’s on a real computer.
A URL gives the exact address of a web resource.
A VLAN separates networks logically without new hardware.
An operating system controls hardware and runs applications.
Cybersecurity protects systems from attacks and prevents unauthorized access.
Cache stores data temporarily to make future access faster.
The kernel controls hardware and manages system resources.
A load balancer spreads traffic across servers to keep them stable.
Ethernet is a wired method to connect devices in a network.
A byte contains 8 bits and often represents one character.
A framework gives developers tools to build apps faster.
RAM stores temporary data used by active programs.
A thread is a sequence of tasks running inside a program.
JavaScript adds interactivity to websites and runs in browsers.
A port is a network access point for specific services.
Machine learning lets systems learn from data to improve themselves.
Bandwidth measures how much information or data can move through a network in a second.
CSS controls how web content looks and is applied to HTML.
A shell is a command interface for controlling a system.
A server responds to network requests from other computers.
A Boolean is a data type that only has two values: true or false.
An API lets software talk to other programs and defines how they interact.
Firmware is permanent software that controls hardware behavior.
A pixel is the smallest part of a digital image.
The UI is what users see and interact with on a system.
A packet carries data across a network in small units.
Git tracks changes in code and helps with version control.
HTTP lets browsers request and receive web pages.
YAML formats data simply for configuration files.
A token represents identity and is used in security.
An IP address identifies a device on a network uniquely.
NoSQL databases handle unstructured or large-scale data.
A proxy server forwards user requests to hide identity.
Python is easy to learn and used in many fields.
SQL is used to manage and query database information.
Docker uses containers to run software the same everywhere.
A bug is an error in software that causes it to behave incorrectly.
Phishing tricks users into giving up personal data.
HTTPS encrypts data during website communication for safety.
An SDK gives developers tools to build software.
A snippet is a small reusable piece of code.
A web server hosts websites and sends pages to browsers.
Open source software is free to view and modify.
A ping tests if another computer can be reached.
Encryption turns data into a code to keep it secure.
Wi-Fi connects devices wirelessly to a local network."""

long_given = """HTTP lets browsers request and receive web pages.
A pixel is the smallest part of a digital image.
A load balancer spreads traffic across servers to keep them stable.
Firmware is permanent software that controls hardware behavior.
REST uses HTTP to send data between systems.
An SDK gives developers tools to build software.
YAML formats data simply for configuration files.
Docker uses containers to run software the same everywhere.
A port is a network access point for specific services.
A packet carries data across a network in small units.
Data mining finds patterns in large sets of information.
Bandwidth measures how much information or data can move through a network in a second.
An operating system controls hardware and runs applications.
A network connects computers so they can share information.
Phishing tricks users into giving up personal data.
A server responds to network requests from other computers.
A shell is a command interface for controlling a system.
A thread is a sequence of tasks running inside a program.
Wi-Fi connects devices wirelessly to a local network.
An API lets software talk to other programs and defines how they interact.
CSS controls how web content looks and is applied to HTML.
Cache stores data temporarily to make future access faster.
RAM stores temporary data used by active programs.
Object-oriented programming uses objects and classes to organize code.
A ping tests if another computer can be reached.
A Boolean is a data type that only has two values: true or false.
A token represents identity and is used in security.
Cybersecurity protects systems from attacks and prevents unauthorized access.
A URL gives the exact address of a web resource.
A byte contains 8 bits and often represents one character.
The UI is what users see and interact with on a system.
A framework gives developers tools to build apps faster.
SQL is used to manage and query database information.
An IP address identifies a device on a network uniquely.
Encryption turns data into a code to keep it secure.
Git tracks changes in code and helps with version control.
A bug is an error in software that causes it to behave incorrectly.
Ethernet is a wired method to connect devices in a network.
A web server hosts websites and sends pages to browsers.
NoSQL databases handle unstructured or large-scale data.
Python is easy to learn and used in many fields.
The kernel controls hardware and manages system resources.
A snippet is a small reusable piece of code.
Open source software is free to view and modify.
HTTPS encrypts data during website communication for safety.
A proxy server forwards user requests to hide identity.
JavaScript adds interactivity to websites and runs in browsers.
Machine learning lets systems learn from data to improve themselves.
A VLAN separates networks logically without new hardware.
A virtual machine runs software like it’s on a real computer."""


# Test for long text comparison
# Expected behavior: Tests that the function can handle longer text inputs
def test_long_texts():
    """Test F1 score with longer text inputs - verifies handling of extended content"""
    texts_expect_f1_equal(long_expected, long_given, 1)
