# Package manager design

## Goals
- School-safe app installation
- Signed packages and trust levels
- Group rollout for labs and classrooms
- Cross-architecture support

## Core commands
- `safepkg install <package>`
- `safepkg update`
- `safepkg audit`
- `safepkg policy apply <profile>`

## Package metadata
- package name
- source
- compatibility profile
- safe-by-default permissions
- classroom policy tags
