const core = require("@actions/core");
const github = require("@actions/github");

const pattern = /^([mM]erge .*)$|(^((build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)!?: .+)((\n\n(.+)\n\n)((BREAKING CHANGE|DEPRECATED)(: )(.+)\n\n(.+)\n\n\n)?(resolve[ds]? \#[A-Z0-9\-]+|fix(ed|es)? \#[A-Z0-9\-]+|close[ds]? \#[A-Z0-9\-]+)((, )(resolve[ds]? \#[A-Z0-9\-]+|fix(ed|es)? \#[A-Z0-9\-]+|close[ds]? \#[A-Z0-9\-]+))?)?$)|(^revert: ((build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)!?: .+)(\n\n(This reverts commit [a-z0-9]{40}\..*)\n\n)(fix(ed|es)? \#[A-Z0-9\-]+)((, )(fix(ed|es)? \#[A-Z0-9\-]+))?$)/;
const restClient = github.getOctokit(core.getInput('token'));

restClient.rest.pulls.listCommits(
    {
        owner: "dan1hc",
        repo: "ft3",
        per_page: 100,
        pull_number: github.context.payload.pull_request.number
        }
    ).then((response) => {
        if (response.data.length >= 100) {
            core.setFailed("Pull request must contain less than 100 commits.");
        } else {
            response.data.every((record) => {
                var commit = record.commit;
                console.log(`COMMITTER: ${commit.committer.name}`);
                console.log(`MESSAGE: ${commit.message}`);
                if (
                    commit.committer.name == "GitHub"
                    || commit.committer.name == "github-actions"
                    || pattern.test(commit.message)
                    ) {
                    console.log("VALID");
                    console.log("");
                    return true
                } else {
                    core.setFailed(`INVALID: ${commit.message}`);
                    return false
                };
            });
        };
    }, (error) => {
        core.setFailed(error);
        }
    );
