# Contributing

Create a feature branch from current `master` and open a pull request targeting
`master`. This applies to maintainers and automated dependency updates alike.

Before merging, update the branch with `master` and wait for all required CI
checks to pass. Reviewer approval is optional. Merge using **Squash and merge**;
GitHub deletes the merged feature branch automatically. Protection applies to
administrators, with no bypass actors, and blocks force pushes and deletion of
`master`.

Dependabot checks supported dependency manifests weekly and assigns its pull
requests to `micknudsen`. Review dependency updates through the same PR and CI
process. Keep Python metadata, development environments, and Conda recipe
constraints consistent; the Conda updater monitors environment files, not
`meta.yaml` recipes. Preserve intentional runtime compatibility constraints.
Dependencies installed only in workflow shell commands need explicit review.

Dependabot alerts and security updates are enabled separately in GitHub.
The active **Protect master** ruleset and repository merge settings enforce this
policy; committed files alone do not enforce branch protection. When renaming
or adding CI jobs, update the required checks to match successfully observed
check names before merging.
