# Code Planning

When deciding how to implement code, stop at the first rung that holds:

- *Does this need to exist at all?* Speculative need = skip it, say so in one line. (YAGNI)
- *Stdlib does it? Use it.
- *Native platform feature covers it?* <input type="date"> over a picker lib, CSS over JS, DB constraint over app code.
- *Already-installed dependency solves it?* Use it. Never add a new one for what a few lines can do.
- *Available 3rd party dependency* Suggest it to the user; don't reinvent the wheel.
- *Can it be one line?* Do it in one line.

If we have to build it ourselves, build only the minimum that is correct and secure. Don't cut corners on quality, and don't over-engineer the problem.

