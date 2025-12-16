[Compare the full difference.](https://github.com/callowayproject/bump-my-version/compare/1.2.4...1.2.5)

### Fixes

- Refactor: Simplify Mercurial test skip condition using `pytest.mark.skipif`. [a596f61](https://github.com/callowayproject/bump-my-version/commit/a596f614688cc91800e21bac61a93239e31ec966)
    
- Fix: Skip Mercurial tests if Mercurial is not available. [bb5ff24](https://github.com/callowayproject/bump-my-version/commit/bb5ff2466276546c80e42f1c6c8d97cc4a22d77b)
    
- Fix README.md's workflow permissions and token usage. [bf4397e](https://github.com/callowayproject/bump-my-version/commit/bf4397e3886a0fec8fcad68de79c73dd6ca2892c)
    
  - Added explicit permissions for `id-token`, `pull-requests`, and `contents` in the build job.
  - Replaced `GH_TOKEN` with `GITHUB_TOKEN` for consistency.
  - Clarified documentation on using personal access tokens (PAT).
  - Removed unused `MANIFEST.in` file.
- Fix outdated link URL in docs leading to a 404. [440300a](https://github.com/callowayproject/bump-my-version/commit/440300aa4d368fcca4be85aaf7245dd355dee25e)
    
### Other

- Compatibility with click 8.3, handle Sentinel values. [554922d](https://github.com/callowayproject/bump-my-version/commit/554922d1e5b44b7218c6b336d61a58b760ebe56f)
    
- [pre-commit.ci] pre-commit autoupdate. [4b844b5](https://github.com/callowayproject/bump-my-version/commit/4b844b56ab85004d06ee779d199ccfa2d3abe576)
    
- Bump actions/download-artifact from 5 to 6 in the github-actions group. [f2613d7](https://github.com/callowayproject/bump-my-version/commit/f2613d7dbee43234677bb7e84660da89d047542d)
    
  Bumps the github-actions group with 1 update: [actions/download-artifact](https://github.com/actions/download-artifact).


  Updates `actions/download-artifact` from 5 to 6
  - [Release notes](https://github.com/actions/download-artifact/releases)
  - [Commits](https://github.com/actions/download-artifact/compare/v5...v6)

  ---
  **updated-dependencies:** - dependency-name: actions/download-artifact
dependency-version: '6'
dependency-type: direct:production
update-type: version-update:semver-major
dependency-group: github-actions

  **signed-off-by:** dependabot[bot] <support@github.com>

- Bump python from 3.12-slim-bookworm to 3.14-slim-bookworm. [1d1d0fe](https://github.com/callowayproject/bump-my-version/commit/1d1d0fe29249b2ee2782e203197d4185fe30b1a3)
    
  Bumps python from 3.12-slim-bookworm to 3.14-slim-bookworm.

  ---
  **updated-dependencies:** - dependency-name: python
dependency-version: 3.14-slim-bookworm
dependency-type: direct:production

  **signed-off-by:** dependabot[bot] <support@github.com>

- [pre-commit.ci] pre-commit autoupdate. [778b8b5](https://github.com/callowayproject/bump-my-version/commit/778b8b5725be97bf4b0c0b4dca4c96fab26efc83)
    
  **updates:** - [github.com/astral-sh/ruff-pre-commit: v0.13.2 → v0.14.5](https://github.com/astral-sh/ruff-pre-commit/compare/v0.13.2...v0.14.5)

### Updates

- Remove unused Python inventory references from `mkdocs.yml`. [21a0c6e](https://github.com/callowayproject/bump-my-version/commit/21a0c6e0d1a163de4f337dd560b6cf0cd9277007)
    
- Remove Python 3.8 support and comment out Mercurial installation steps on Windows in GitHub Actions workflow. [3ec922b](https://github.com/callowayproject/bump-my-version/commit/3ec922b175b85dc1425788c01dd9046c71284d30)
    
