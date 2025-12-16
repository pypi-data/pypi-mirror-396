module.exports = {
  branches: ['main'],
  plugins: [
    [
      '@semantic-release/commit-analyzer',
      {
        // Commit format is enforced by pr-title-automations.yml workflow
        // Using conventionalcommits preset to handle BREAKING CHANGE in footer
        //
        // Release types:
        // - [feat] PL-1234: Description     → Minor release
        // - [fix] PL-1234: Description      → Patch release
        // - [docs]/[chore]/etc.             → No release
        //
        // Breaking changes (major release):
        // [fix] PL-1234: Description
        //
        // BREAKING CHANGE: Description of the breaking change
        //
        // (Footer must be on separate line after blank line)
        preset: 'conventionalcommits',
        parserOpts: {
          headerPattern: /^\[([^\]]+)\]\s+([^:]+):\s+(.+)$/,
          headerCorrespondence: ['type', 'scope', 'subject']
        },
        releaseRules: [
          { breaking: true, release: 'major' },
          { type: 'feat', release: 'minor' },
          { type: 'fix', release: 'patch' },
          { type: 'perf', release: 'patch' },
          { type: 'revert', release: 'patch' },
          { type: 'docs', release: false },
          { type: 'style', release: false },
          { type: 'refactor', release: false },
          { type: 'test', release: false },
          { type: 'build', release: false },
          { type: 'ci', release: false },
          { type: 'chore', release: false }
        ]
      }
    ],
    [
      '@semantic-release/release-notes-generator',
      {
        preset: 'conventionalcommits',
        parserOpts: {
          headerPattern: /^\[([^\]]+)\]\s+([^:]+):\s+(.+)$/,
          headerCorrespondence: ['type', 'scope', 'subject']
        }
      }
    ],
    [
      '@semantic-release/github',
      {
        successComment: false,
        failComment: false
      }
    ]
  ]
};
