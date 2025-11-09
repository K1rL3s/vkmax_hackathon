module.exports = {
  api: {
    input: './src/lib/api/schema.yaml',
    output: {
      target: './src/lib/api/gen.ts',
      mode: 'tags-split',
      override: {
        mutator: {
          path: './src/lib/api/client.ts',
          name: 'request',
        },
      },
    },
  },
}
