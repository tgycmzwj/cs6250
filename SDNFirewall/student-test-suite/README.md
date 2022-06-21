# cs6250_SDN_Project

Originally developed by htian66 in Spring 2021 (approved for distribution)
Adapted for testing Summer 2022

Changelog:
1.  sdn-topology changed IP addresses for hosts and adding an other2 for testing world
2.  testcases.txt updated to match ruleset for Fall 2021.  The testcases.txt as specified in the main directory will be
    same used by the AutoGrader for the first set.  Additional tests will be used by the autograde in a manner similar, but
    not the same as used in the extra directory.  (Jeffrey)

Usage:

1. Download this repo.
2. Copy your `sdn-firewall.py` and `configure.pol` into this directory. 
3. Run `./start-firewall.sh configure.pol` as usual.
4. Open a new window, run `sudo python test_all.py`. 
5. Total passed cases are calculated. Wrong cases will be displayed. For example, `2: us1 -> hq1 with U at 53, should be True, current False` means the connection from client us1 to host hq1 using UDP at hq1 53 port is failed, which should be successful. The first number is the index (0-based) of testcases. 

Note:

2. One testcase in the `testcases.txt` file is given here: `us1 hq1 U 53 True` -> us1 client should be able to access hq1 host with TCP protocol at port 80. Please pull request to fill the `testcases.txt` file.
3. For goal 3, `P` is used in `testcaeses.txt` to represent `ping`.
4. `test-server.py` and `test-client.py` are slighted modified from the original version to support `GRE` protocol testing. 

<b><i>If you want to test your `sdn-firewall.py` robustness, copy your `sdn-firewall.py` to `extra` directory. Go to this directory and do (1) `./start-firewall.sh configure.pol` and then (2) `sudo python test_all.py` </i></b> 

Note:
1. The format/content of `testcases.txt`, `sdn-topology.py` and `test_all.py` in the `extra` directory is different (for src port testing). 
2. Note there is a minor error in `test-client.py`. See piazza post [here](https://piazza.com/class/kie4njlr1ki6yg?cid=331_f21). 
