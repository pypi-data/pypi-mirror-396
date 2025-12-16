# Changelog

## 1.3.1 (2025-12-13)

Full Changelog: [v1.3.0...v1.3.1](https://github.com/Bread-Technologies/Bread-SDK/compare/v1.3.0...v1.3.1)

### Features

* **api:** fixed mcp access and added download function ([f21ce8c](https://github.com/Bread-Technologies/Bread-SDK/commit/f21ce8c117c05e2780311635f7d7336ebb56df17))

## 1.3.0 (2025-12-12)

Full Changelog: [v1.2.0...v1.3.0](https://github.com/Bread-Technologies/Bread-SDK/compare/v1.2.0...v1.3.0)

### Features

* **api:** added deprecated support for stim prompts ([63ae951](https://github.com/Bread-Technologies/Bread-SDK/commit/63ae95185bf0d403cb7ade36bdac46fae96e7c17))
* **api:** added metrics and tree endpoints, updated list repos w/ metadata ([3444189](https://github.com/Bread-Technologies/Bread-SDK/commit/34441893901b83177c83e59c0f17e44ee97075de))
* **api:** added post support ([42bab78](https://github.com/Bread-Technologies/Bread-SDK/commit/42bab7861b8ad04c4b5f2f0008f98f517e11e9f6))
* **api:** added recipe support ([ee67769](https://github.com/Bread-Technologies/Bread-SDK/commit/ee67769165f59419b4b8047c9b2c31f3705140fe))
* **api:** bake job now returns status instead of message ([0b53bef](https://github.com/Bread-Technologies/Bread-SDK/commit/0b53bef3428a2765415f6085f17ea86b921e7482))
* **api:** changing security in stainless config to http bearer ([e7df695](https://github.com/Bread-Technologies/Bread-SDK/commit/e7df6959dc2bf74f8aa5bfe22a88913e3c0cd369))
* **api:** fixed bearer auth setup ([6abbdb8](https://github.com/Bread-Technologies/Bread-SDK/commit/6abbdb8380e2be91222899abfcc37402aea4491d))
* **api:** manual updates ([6755ec2](https://github.com/Bread-Technologies/Bread-SDK/commit/6755ec2d1e79c25039668bdcbf26478e2723e354))
* **api:** manual updates ([5696786](https://github.com/Bread-Technologies/Bread-SDK/commit/56967869cdfa361a0a92e0e99a7f3d82925b7510))
* **api:** manual updates ([4d7a9f1](https://github.com/Bread-Technologies/Bread-SDK/commit/4d7a9f1a7f54c27c8f1b8b0bd5cd34569d29a436))
* **api:** manual updates ([08fa257](https://github.com/Bread-Technologies/Bread-SDK/commit/08fa25736626d45a5fb54798e651995abdb3ec7c))
* **api:** manual updates ([2cd4b14](https://github.com/Bread-Technologies/Bread-SDK/commit/2cd4b14186d50f3efcbe24acc46d826d5c436402))
* **api:** manual updates ([de44272](https://github.com/Bread-Technologies/Bread-SDK/commit/de44272a271f1488b81c4ba4cf9d67d7d46d3605))
* **api:** manual updates ([fbc0969](https://github.com/Bread-Technologies/Bread-SDK/commit/fbc09694fccb65adf90d822d992e27795f26befd))
* **api:** manual updates ([b9b4957](https://github.com/Bread-Technologies/Bread-SDK/commit/b9b495706bea8356e956dad77f43548c18821e99))
* **api:** manual updates ([5ff779a](https://github.com/Bread-Technologies/Bread-SDK/commit/5ff779ac725676ae017177030f7c0b46999dc042))
* **api:** manual updates ([69aa5da](https://github.com/Bread-Technologies/Bread-SDK/commit/69aa5da1c9f710a0158abcc6e4c2a197270f97fd))
* **api:** manual updates ([1465b5a](https://github.com/Bread-Technologies/Bread-SDK/commit/1465b5a2b027d5e6fa76cd642bb6dac6d3f157e1))
* **api:** manual updates ([330ddfe](https://github.com/Bread-Technologies/Bread-SDK/commit/330ddfec8daf7ed4dcf69e26e081df6a31bedfff))
* **api:** manual updates ([badb038](https://github.com/Bread-Technologies/Bread-SDK/commit/badb03885f8405358a3ffb96e8e6df74c3f2ca81))
* **api:** manual updates ([f24d265](https://github.com/Bread-Technologies/Bread-SDK/commit/f24d26590b53759fccebe11e88da48ee55dae1b8))
* **api:** manual updates ([d1350fc](https://github.com/Bread-Technologies/Bread-SDK/commit/d1350fc301666d93c7bb477170ceab02e2239968))
* **api:** manual updates ([4da8b41](https://github.com/Bread-Technologies/Bread-SDK/commit/4da8b41ab8482d654e876993f3ddf3536e8312bf))
* **api:** manual updates ([4f77094](https://github.com/Bread-Technologies/Bread-SDK/commit/4f770946e0aed08a4522afcbb93565c6ebc5317b))
* **api:** manual updates ([3cfe460](https://github.com/Bread-Technologies/Bread-SDK/commit/3cfe460d767d96ebf276de5cb6046125e91f74f1))
* **api:** manual updates to pydantic types for model_name, loss and max_tokens in generators ([c3065cd](https://github.com/Bread-Technologies/Bread-SDK/commit/c3065cdce54b3d74370070ec168dc20c58f06b4a))
* **api:** manual updates to test prompt format ([2749f06](https://github.com/Bread-Technologies/Bread-SDK/commit/2749f06b953d7daf177b87f1263804aae9e3037f))
* **api:** testing bearer auth ([43188cb](https://github.com/Bread-Technologies/Bread-SDK/commit/43188cb7ec7c9bf5477c21b81cae4a9383e50158))
* **api:** updated targetConfigBase to accept input config ([1547c06](https://github.com/Bread-Technologies/Bread-SDK/commit/1547c06a0ad91383bcbcf6dcbb6d2e2eb84de636))
* **api:** updated tool support for prompts ([9af469e](https://github.com/Bread-Technologies/Bread-SDK/commit/9af469e206552e8a68c0e88c13fc5d47a47451c6))


### Bug Fixes

* compat with Python 3.14 ([74f929b](https://github.com/Bread-Technologies/Bread-SDK/commit/74f929bce0e9896495909e4ed80d4cefbc0e8d8b))
* **compat:** update signatures of `model_dump` and `model_dump_json` for Pydantic v1 ([40ccbb7](https://github.com/Bread-Technologies/Bread-SDK/commit/40ccbb71ba8bd259066a73a6652e0398e6e5026b))
* ensure streams are always closed ([0fa0d82](https://github.com/Bread-Technologies/Bread-SDK/commit/0fa0d82120164cdbe4bb9edbda24d70bcaf5f8e0))
* **types:** allow pyright to infer TypedDict types within SequenceNotStr ([9be504b](https://github.com/Bread-Technologies/Bread-SDK/commit/9be504b95a4be52fdeaa3dcbc81fee9360fa4dcd))


### Chores

* add missing docstrings ([5047836](https://github.com/Bread-Technologies/Bread-SDK/commit/5047836a7c60ed99ab27ceabbeb1530ad1905485))
* add Python 3.14 classifier and testing ([7c0a559](https://github.com/Bread-Technologies/Bread-SDK/commit/7c0a559db8bbd44fe99c769d3c3e37c96a529b84))
* **deps:** mypy 1.18.1 has a regression, pin to 1.17 ([1f82e08](https://github.com/Bread-Technologies/Bread-SDK/commit/1f82e086efc0b63c0c69159b5f792d7f0b435144))
* **docs:** use environment variables for authentication in code snippets ([ad683e8](https://github.com/Bread-Technologies/Bread-SDK/commit/ad683e8265c3e988cc26b96e353122c3e3542090))
* **internal/tests:** avoid race condition with implicit client cleanup ([4b021ce](https://github.com/Bread-Technologies/Bread-SDK/commit/4b021ce64551fb1b5528fcc321a780e1e7a08028))
* **internal:** grammar fix (it's -&gt; its) ([ec230ec](https://github.com/Bread-Technologies/Bread-SDK/commit/ec230ec2a63c3089e54b42169e5b6ac7946b2265))
* **package:** drop Python 3.8 support ([078e399](https://github.com/Bread-Technologies/Bread-SDK/commit/078e39907c73341e32552f33fc2b326142118d8e))
* update lockfile ([77076d4](https://github.com/Bread-Technologies/Bread-SDK/commit/77076d4c85b90d6dec5ceeba2cd795593e65784a))
* update SDK settings ([2ea5829](https://github.com/Bread-Technologies/Bread-SDK/commit/2ea58296bde31c8a6f9e8f3626dc725e8a7f424c))
* update SDK settings ([008f674](https://github.com/Bread-Technologies/Bread-SDK/commit/008f6745adcd1343bee43a34dfc47a2955a496b0))

## 1.2.0 (2025-11-25)

Full Changelog: [v1.1.3...v1.2.0](https://github.com/Bread-Technologies/Bread-SDK/compare/v1.1.3...v1.2.0)

### Features

* **api:** added post support ([42bab78](https://github.com/Bread-Technologies/Bread-SDK/commit/42bab7861b8ad04c4b5f2f0008f98f517e11e9f6))
* **api:** added recipe support ([ee67769](https://github.com/Bread-Technologies/Bread-SDK/commit/ee67769165f59419b4b8047c9b2c31f3705140fe))
* **api:** changing security in stainless config to http bearer ([e7df695](https://github.com/Bread-Technologies/Bread-SDK/commit/e7df6959dc2bf74f8aa5bfe22a88913e3c0cd369))
* **api:** fixed bearer auth setup ([6abbdb8](https://github.com/Bread-Technologies/Bread-SDK/commit/6abbdb8380e2be91222899abfcc37402aea4491d))
* **api:** manual updates ([6755ec2](https://github.com/Bread-Technologies/Bread-SDK/commit/6755ec2d1e79c25039668bdcbf26478e2723e354))
* **api:** manual updates ([5696786](https://github.com/Bread-Technologies/Bread-SDK/commit/56967869cdfa361a0a92e0e99a7f3d82925b7510))
* **api:** testing bearer auth ([43188cb](https://github.com/Bread-Technologies/Bread-SDK/commit/43188cb7ec7c9bf5477c21b81cae4a9383e50158))


### Chores

* add Python 3.14 classifier and testing ([7c0a559](https://github.com/Bread-Technologies/Bread-SDK/commit/7c0a559db8bbd44fe99c769d3c3e37c96a529b84))

## 1.1.3 (2025-11-14)

Full Changelog: [v1.1.0...v1.1.3](https://github.com/Bread-Technologies/Bread-SDK/compare/v1.1.0...v1.1.3)

### Features

* **api:** added deprecated support for stim prompts ([63ae951](https://github.com/Bread-Technologies/Bread-SDK/commit/63ae95185bf0d403cb7ade36bdac46fae96e7c17))
* **api:** bake job now returns status instead of message ([0b53bef](https://github.com/Bread-Technologies/Bread-SDK/commit/0b53bef3428a2765415f6085f17ea86b921e7482))
* **api:** manual updates to pydantic types for model_name, loss and max_tokens in generators ([c3065cd](https://github.com/Bread-Technologies/Bread-SDK/commit/c3065cdce54b3d74370070ec168dc20c58f06b4a))
* **api:** updated targetConfigBase to accept input config ([1547c06](https://github.com/Bread-Technologies/Bread-SDK/commit/1547c06a0ad91383bcbcf6dcbb6d2e2eb84de636))

## 1.1.0 (2025-11-12)

Full Changelog: [v1.0.0...v1.1.0](https://github.com/Bread-Technologies/Bread-SDK/compare/v1.0.0...v1.1.0)

### Features

* **api:** updated tool support for prompts ([9af469e](https://github.com/Bread-Technologies/Bread-SDK/commit/9af469e206552e8a68c0e88c13fc5d47a47451c6))


### Bug Fixes

* **compat:** update signatures of `model_dump` and `model_dump_json` for Pydantic v1 ([40ccbb7](https://github.com/Bread-Technologies/Bread-SDK/commit/40ccbb71ba8bd259066a73a6652e0398e6e5026b))

## 1.0.0 (2025-11-11)

Full Changelog: [v1.0.0...v1.0.0](https://github.com/Bread-Technologies/Bread-SDK/compare/v1.0.0...v1.0.0)

### Features

* **api:** manual updates ([4d7a9f1](https://github.com/Bread-Technologies/Bread-SDK/commit/4d7a9f1a7f54c27c8f1b8b0bd5cd34569d29a436))
* **api:** manual updates ([08fa257](https://github.com/Bread-Technologies/Bread-SDK/commit/08fa25736626d45a5fb54798e651995abdb3ec7c))

## 1.0.0 (2025-11-11)

Full Changelog: [v1.1.0...v1.0.0](https://github.com/Bread-Technologies/Bread-SDK/compare/v1.1.0...v1.0.0)

### Features

* **api:** manual updates ([2cd4b14](https://github.com/Bread-Technologies/Bread-SDK/commit/2cd4b14186d50f3efcbe24acc46d826d5c436402))

## 1.1.0 (2025-11-11)

Full Changelog: [v1.0.0...v1.1.0](https://github.com/Bread-Technologies/Bread-SDK/compare/v1.0.0...v1.1.0)

### Features

* **api:** manual updates ([de44272](https://github.com/Bread-Technologies/Bread-SDK/commit/de44272a271f1488b81c4ba4cf9d67d7d46d3605))


### Bug Fixes

* compat with Python 3.14 ([74f929b](https://github.com/Bread-Technologies/Bread-SDK/commit/74f929bce0e9896495909e4ed80d4cefbc0e8d8b))


### Chores

* **package:** drop Python 3.8 support ([078e399](https://github.com/Bread-Technologies/Bread-SDK/commit/078e39907c73341e32552f33fc2b326142118d8e))

## 1.0.0 (2025-11-05)

Full Changelog: [v1.1.0...v1.0.0](https://github.com/Bread-Technologies/Bread-SDK/compare/v1.1.0...v1.0.0)

### Features

* **api:** manual updates ([fbc0969](https://github.com/Bread-Technologies/Bread-SDK/commit/fbc09694fccb65adf90d822d992e27795f26befd))

## 1.1.0 (2025-11-04)

Full Changelog: [v1.0.0...v1.1.0](https://github.com/Bread-Technologies/Bread-SDK/compare/v1.0.0...v1.1.0)

### Features

* **api:** manual updates ([b9b4957](https://github.com/Bread-Technologies/Bread-SDK/commit/b9b495706bea8356e956dad77f43548c18821e99))

## 1.0.0 (2025-11-04)

Full Changelog: [v0.1.0...v1.0.0](https://github.com/Bread-Technologies/Bread-SDK/compare/v0.1.0...v1.0.0)

### Features

* **api:** manual updates ([5ff779a](https://github.com/Bread-Technologies/Bread-SDK/commit/5ff779ac725676ae017177030f7c0b46999dc042))


### Chores

* **internal:** grammar fix (it's -&gt; its) ([ec230ec](https://github.com/Bread-Technologies/Bread-SDK/commit/ec230ec2a63c3089e54b42169e5b6ac7946b2265))
* update SDK settings ([2ea5829](https://github.com/Bread-Technologies/Bread-SDK/commit/2ea58296bde31c8a6f9e8f3626dc725e8a7f424c))

## 0.1.0 (2025-11-04)

Full Changelog: [v0.0.1...v0.1.0](https://github.com/Bread-Technologies/Bread-SDK/compare/v0.0.1...v0.1.0)

### Features

* **api:** manual updates ([69aa5da](https://github.com/Bread-Technologies/Bread-SDK/commit/69aa5da1c9f710a0158abcc6e4c2a197270f97fd))
* **api:** manual updates ([1465b5a](https://github.com/Bread-Technologies/Bread-SDK/commit/1465b5a2b027d5e6fa76cd642bb6dac6d3f157e1))
* **api:** manual updates ([330ddfe](https://github.com/Bread-Technologies/Bread-SDK/commit/330ddfec8daf7ed4dcf69e26e081df6a31bedfff))
* **api:** manual updates ([badb038](https://github.com/Bread-Technologies/Bread-SDK/commit/badb03885f8405358a3ffb96e8e6df74c3f2ca81))
* **api:** manual updates ([f24d265](https://github.com/Bread-Technologies/Bread-SDK/commit/f24d26590b53759fccebe11e88da48ee55dae1b8))
* **api:** manual updates ([d1350fc](https://github.com/Bread-Technologies/Bread-SDK/commit/d1350fc301666d93c7bb477170ceab02e2239968))
* **api:** manual updates ([4da8b41](https://github.com/Bread-Technologies/Bread-SDK/commit/4da8b41ab8482d654e876993f3ddf3536e8312bf))
* **api:** manual updates ([4f77094](https://github.com/Bread-Technologies/Bread-SDK/commit/4f770946e0aed08a4522afcbb93565c6ebc5317b))
* **api:** manual updates ([3cfe460](https://github.com/Bread-Technologies/Bread-SDK/commit/3cfe460d767d96ebf276de5cb6046125e91f74f1))
* **api:** manual updates to test prompt format ([2749f06](https://github.com/Bread-Technologies/Bread-SDK/commit/2749f06b953d7daf177b87f1263804aae9e3037f))


### Chores

* **internal/tests:** avoid race condition with implicit client cleanup ([4b021ce](https://github.com/Bread-Technologies/Bread-SDK/commit/4b021ce64551fb1b5528fcc321a780e1e7a08028))
* update SDK settings ([008f674](https://github.com/Bread-Technologies/Bread-SDK/commit/008f6745adcd1343bee43a34dfc47a2955a496b0))
