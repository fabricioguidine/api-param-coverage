#!/bin/sh
# Auto-generated rebase script
exec < /dev/tty
git rebase -i --root <<'REBASE_EOF'
pick 36b0af335f45c8c3d689f55baeba36bcd97ccb3a chore: initial commit
pick b9aeedda5767e6d038c2746ce73e7ae948e160b4 feat: add brd system and analytics tracking
squash 09b2dfb3744116d29f4835906b5813a9ca8838a2 refactor: reorganize project structure and add tests
squash 3fe7e2fd7ebb3ab07bf0fc6fd562362e5a636869 chore: clean up .gitignore for cursor files
squash 6a36f35d29f8fd989c8b9c30be10e59d1f9ab0cd refactor: reorganize brd workflow architecture
squash d8f7c62a9c7a45156737c5b70e5c7ab55e496e7d refactor: update .gitignore for brd files
squash 991f885f849219a947a7e600a01c24e0c688ac07 refactor: reorganize output to docs/output
squash d4dfdf720b6a9ba3c4a134a5fddfdfd7b1174177 refactor: update readme and script paths
squash 810b1cc24b0ed5d18236f4b508cffe14280ff564 refactor: update readme configuration references
squash 80b7b4fa88831e3b6f4fbc24e0479050de9a1cbe feat: add readme for output structure
squash be67ee50b2f8c7138d11ee739acbed4bac267d69 chore: organize outputs by execution runs
squash c5acf20f0a4551cfe9c7858b8833efdfb15d015c feat: add analytics_dir parameter to llmprompter
squash 16582329e21ae2a89702249177f36951a5a8d63c chore: use run-specific output directories
squash d281acfb3a8d203d7bbaba87d5baae37947c1618 refactor: update readme for run-based output
squash a41f79f7f213e3d80d19f13bf7927e80b2f07d90 chore: preserve spaces in csv step parsing
squash 28c9bbc113bfe5790e46e382375e4720b523762e fix: remove duplicate csvgenerator initialization
squash 3293e239f4653e2060aed9bd9e714818c6deea4b refactor: reorganize docs with timestamp structure
pick 2cb41dcc4bc07ae59749512c0eba409e63b69e3e docs: improve readme formatting and structure
pick e2864a0652ea112a0f4be71e564f9dace99b16d8 feat: add comprehensive tests for brd generator module
squash 9051a21946cb39076131208e4c9841496b1e3d86 refactor: update next steps with completed brd generator tests and validator
squash 0e7b1e51e5b40bda8e5e70903f627ff778e11747 feat: add edge case tests for brd validator and parser modules
squash 76a171480903f46e6fdd3ed4ff1fb3f29481190f fix: remove completed items from next steps roadmap
squash 5a7baf2ccd7fb818843c9932878e13c3a140bc98 refactor: reorganize docs folder and move output to root
pick d6e8ac98c8fc6487b842c21152b50c350a55206f feat: implement latex parser module with brd integration
squash 7bc436c3e394e7cc94750efe56b9ef05daaa218f feat: implement test coverage analysis module
squash e0c6fb00cc24ab50e720397ea57c8e86165edc8c feat: implement analytics dashboard with aggregator and cost analysis
squash 46c40645ba9da10c7b2b4eea7f7c00f3e137121b fix: remove completed items from next steps roadmap
squash 4fb7927eca44790d1e46ef7773cb1be7ba580ee2 feat: implement multi-format exporter for jira testrail azure devops json and html
squash f5e34848a22280dc7bd480d85144c347371634f0 chore: integrate multi-format exporter into main workflow
squash 2d3eeead88f8a7ac1063daa2683346d3a650242e refactor: update readme and tests for multi-format export feature
squash 0143edb893a48bed72e87ace7954fae2da12e166 feat: add multi-format exporter details to readme
squash 57615e5f396c2d705821621f6a44eae7926c964f feat: implement configuration management with yaml json and environment support
squash d19877ff15b29122b257bbfc26155cf8af7cb9a5 refactor: update project documentation with all new features
squash b9a5bce37b44ddd810b97aa8fa71656823e80e79 refactor: update readme project structure with all modules
squash 5225374d4bc516f4f126b86990572bc3a37092c9 feat: implement interactive cli with progress bars and error recovery
squash a3be691488b44d4d4ee800d2d6ed36cb931d6c70 feat: add interactive cli features to readme
squash 1122d6cfa80a25e713e2ff59e7c65f3ecd475401 feat: add missing re import in aggregator and exporter
squash bd1c7d92197a51628a757f13d1a246dea6bd6da7 chore: improve code quality with method refactoring error messages and type hints
squash aff871902eec7c331a036381310d3ae5ac5fb7cf feat: add missing list type hints in brd modules
squash 3dc126902d79701d766a77703d327eaa967d3823 chore: extract shared utilities and consolidate duplicate code
squash 23a04d48add4afe7e967fc8c12c1386f54795f86 feat: add missing list import in brd parser
squash 75f2f0cd15405b7f2e50a1196f478fdbdeaa6a89 refactor: update tests to use shared json extraction utility
squash c8bcd5bc911a787660cc353c4871f6d4b7a65832 feat: add comprehensive user guide developer guide architecture and api documentation
squash 3b9929a445a56fdffced7fcaf553abfd0373661f chore: extract workflow functions from main.py into workflow module
squash 511432162b78f6bbda3fffaf6d0c7bc6dd668e0e chore: correct import paths for constants in workflow modules
squash bc955732e7972aec60ec9d00c71be0f611953249 chore: use correct constant names from constants module
squash 2a38874b412f17c5758f0e55725db9f14ef0530b feat: add performance profiling caching optimization and parallel processing
squash e77c44b785f6c44e57d54d25d35f9eab840608f8 feat: add missing dict import in parallel module
squash c09d81706702de49d8a0d13fc88e720546c726ff refactor: update default schemas directory and remove next steps file
squash c5f28c44f433069194a4a20ecd47375f4c9e2be2 refactor: update project status and documentation structure
squash a76dc13b97a0d745db789f95c5cae5175430d9a9 chore: complete project status update and remove outdated sections
squash 55c769920dfd5e58764daace90a9039407a53bf3 chore: finalize project status document cleanup
squash 970979262558a0c01d458b71ff48b5955246e25c refactor: refactor readme: convert modules to table format
squash a0d9092819060cf1455c0f1fe2d8858561c7d92e fix: remove multi-format export, keep csv only
squash 7b0a91178d58afa01a169f4a86c658c107398052 feat: add llm provider detection and one-time api key setup
squash ffa616818f88a6e6d18dfe3eb7304e969a0cb9d1 fix: fix modules overview table: remove empty cells
squash 1bce4c6afb2866b451ede79d2a8102b08355b29c fix: remove large context files to free memory
REBASE_EOF
