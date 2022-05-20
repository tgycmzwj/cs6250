from helper import *
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--sport', help="Enable the source port filter (Default is dest port)", action='store_true', dest="sport", default=False)
parser.add_argument('-p', '--port', dest="port", default='5001')
parser.add_argument('-f', dest="files", nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)
parser.add_argument('-t', '--title', dest="title", default="TCP congestion window (cwnd) timeseries")
parser.add_argument('-H', '--histogram', dest="histogram",
                    help="Plot histogram of sum(cwnd_i)",
                    action="store_true",
                    default=False)

args = parser.parse_args()

def first(lst):
    return [e[0] for e in lst]

def second(lst):
    return [e[1] for e in lst]

def parse_file(f):
    times = defaultdict(list)
    cwnd = defaultdict(list)
    skipped = False
    s_time = None
    with open(f, 'r') as file:
        for l in file:
            if l.strip().startswith("#"):
                continue
            line = l.strip().split('tcp_probe:')
            if s_time is None:
                s_time = float(line[0].split()[-1].split(":")[0])
            timestamp = float(line[0].split()[-1].split(":")[0]) - s_time
            fields = line[1].split()
            if len(fields) != 12:
                skipped = True
                continue
            if not args.sport:
                if fields[1].split('=')[1].split(':')[1] != args.port:
                    continue
            else:
                if fields[0].split('=')[1].split(':')[1] != args.port:
                    continue
            sport = int(fields[0].split('=')[1].split(':')[1])
            times[sport].append(timestamp)

            c = int(fields[6].split('=')[1])
            cwnd[sport].append(c * 1480 / 1024.0)
            if skipped:
                print("Warning, please let a TA know if you see this error message, in the matching project thread on Piazza.")
        return times, cwnd

added = defaultdict(int)
events = []

def plot_cwnds(ax):
    global events
    for f in args.files:
        times, cwnds = parse_file(f)
        for port in sorted(cwnds.keys()):
            t = times[port]
            cwnd = cwnds[port]

            events += list(zip(t, [port]*len(t), cwnd))
            ax.plot(t, cwnd)

    events.sort()
total_cwnd = 0
cwnd_time = []

min_total_cwnd = 10**10
max_total_cwnd = 0
totalcwnds = []

m.rc('figure', figsize=(16, 6))
fig = plt.figure()
plots = 1
if args.histogram:
    plots = 2

axPlot = fig.add_subplot(1, plots, 1)
plot_cwnds(axPlot)

for (t,p,c) in events:
    if added[p]:
        total_cwnd -= added[p]
    total_cwnd += c
    cwnd_time.append((t, total_cwnd))
    added[p] = c
    totalcwnds.append(total_cwnd)

axPlot.plot(first(cwnd_time), second(cwnd_time), lw=2, label="$\sum_i W_i$")
axPlot.grid(True)
#axPlot.legend()
axPlot.set_xlabel("seconds")
axPlot.set_ylabel("cwnd KB")
axPlot.set_title(args.title)

if args.histogram:
    axHist = fig.add_subplot(1, 2, 2)
    n, bins, patches = axHist.hist(totalcwnds, 50, normed=1, facecolor='green', alpha=0.75)

    axHist.set_xlabel("bins (KB)")
    axHist.set_ylabel("Fraction")
    axHist.set_title("Histogram of sum(cwnd_i)")

if args.out:
    print('saving to', args.out)
    plt.savefig(args.out)
else:
    plt.show()
