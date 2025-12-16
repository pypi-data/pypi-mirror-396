# Changelog

## 0.5.0 (2025-12-12)

Full Changelog: [v0.4.0...v0.5.0](https://github.com/adamsteele-sp/searchpilot-python/compare/v0.4.0...v0.5.0)

### Features

* **api:** add bucket URLs CSV key to the Experiment resource ([2e27ef4](https://github.com/adamsteele-sp/searchpilot-python/commit/2e27ef4e878e506e0edc90a4687762fe75839a11))


### Bug Fixes

* compat with Python 3.14 ([66e1dfa](https://github.com/adamsteele-sp/searchpilot-python/commit/66e1dfa83515576863c7afc3494be1580ab31760))
* **compat:** update signatures of `model_dump` and `model_dump_json` for Pydantic v1 ([39e4fac](https://github.com/adamsteele-sp/searchpilot-python/commit/39e4fac5ac6eb4870c90c4426807aae73c0a26a3))
* ensure streams are always closed ([0af5824](https://github.com/adamsteele-sp/searchpilot-python/commit/0af58247858a8b09404ce385b41757dcefe7056c))
* **types:** allow pyright to infer TypedDict types within SequenceNotStr ([ce86879](https://github.com/adamsteele-sp/searchpilot-python/commit/ce86879dd0824ba718eb3503ee8c0b8db64d7cd4))


### Chores

* add Python 3.14 classifier and testing ([c3a0d2e](https://github.com/adamsteele-sp/searchpilot-python/commit/c3a0d2ed1e5485f287daea67cec9660ea1d12a81))
* **deps:** mypy 1.18.1 has a regression, pin to 1.17 ([5cd7abd](https://github.com/adamsteele-sp/searchpilot-python/commit/5cd7abd7e8030d4c8dc646554f064babf8a76b48))
* **docs:** use environment variables for authentication in code snippets ([0818631](https://github.com/adamsteele-sp/searchpilot-python/commit/0818631c5ae376fb93b1ba7069b09dfdec96e24a))
* **package:** drop Python 3.8 support ([c34495d](https://github.com/adamsteele-sp/searchpilot-python/commit/c34495d695a77cd4bdb7c46fc011677724351692))
* update lockfile ([845f535](https://github.com/adamsteele-sp/searchpilot-python/commit/845f5359e1864d8e1d85d5cdfcf4eae01c345454))

## 0.4.0 (2025-11-06)

Full Changelog: [v0.3.0...v0.4.0](https://github.com/adamsteele-sp/searchpilot-python/compare/v0.3.0...v0.4.0)

### Features

* **api:** manual updates ([6eeffcb](https://github.com/adamsteele-sp/searchpilot-python/commit/6eeffcb56f511cfdfad5c62b59ca312535ba3e02))

## 0.3.0 (2025-11-05)

Full Changelog: [v0.2.0...v0.3.0](https://github.com/adamsteele-sp/searchpilot-python/compare/v0.2.0...v0.3.0)

### Features

* **api:** manual updates ([ff1a26e](https://github.com/adamsteele-sp/searchpilot-python/commit/ff1a26ef5673cf47917d32ea07ecefec90f4859e))
* **api:** manual updates ([e47257b](https://github.com/adamsteele-sp/searchpilot-python/commit/e47257ba715ad3b6ed2eb20750b71a8f3eeca6f9))
* **api:** manual updates ([2452848](https://github.com/adamsteele-sp/searchpilot-python/commit/2452848fa25fd5216e7deb569107319a70adfc08))
* **api:** manual updates ([33cbbdd](https://github.com/adamsteele-sp/searchpilot-python/commit/33cbbdd4029cd1c374b4ad9942c49ba2d04e94d3))
* **api:** manual updates ([fa356e9](https://github.com/adamsteele-sp/searchpilot-python/commit/fa356e971ebcb9b68e75db94e11974d018ce1d17))
* **api:** manual updates ([a2bd50a](https://github.com/adamsteele-sp/searchpilot-python/commit/a2bd50ad856c777650684aab5cbf122d97437aa4))


### Bug Fixes

* **client:** close streams without requiring full consumption ([88365a2](https://github.com/adamsteele-sp/searchpilot-python/commit/88365a21382dda42fd2e46788161beba160c7de8))


### Chores

* **internal/tests:** avoid race condition with implicit client cleanup ([96754c5](https://github.com/adamsteele-sp/searchpilot-python/commit/96754c5a4e258fcdd7aa54ba81fb234ca4afb2bf))
* **internal:** grammar fix (it's -&gt; its) ([7dabdbf](https://github.com/adamsteele-sp/searchpilot-python/commit/7dabdbf552ad729697891525f24fd7530605bbc7))
* remove custom code ([a6b593b](https://github.com/adamsteele-sp/searchpilot-python/commit/a6b593bf1ad81f8dc1eae5462ba4ceb8efcc414c))

## 0.2.0 (2025-10-22)

Full Changelog: [v0.0.2...v0.2.0](https://github.com/adamsteele-sp/searchpilot-python/compare/v0.0.2...v0.2.0)

### Features

* **api:** manual updates ([1ad02ae](https://github.com/adamsteele-sp/searchpilot-python/commit/1ad02ae9c61485b794bcb58a32d57b76df115ac2))
* **api:** manual updates ([f93f87a](https://github.com/adamsteele-sp/searchpilot-python/commit/f93f87ac48e31529d52ab2d57f7887e27e234854))
* **api:** manual updates ([cff097d](https://github.com/adamsteele-sp/searchpilot-python/commit/cff097df39a14405d1ac28dabf02ce64e1390f8b))
* change keyword only args on section resource to include account_slug ([00726de](https://github.com/adamsteele-sp/searchpilot-python/commit/00726def877a0991fa4cab8ee2f02f82e7a49c08))


### Chores

* bump `httpx-aiohttp` version to 0.1.9 ([58e5b5e](https://github.com/adamsteele-sp/searchpilot-python/commit/58e5b5ec90dfae8831040c7d5b432a3996d783db))

## 0.0.2 (2025-10-16)

Full Changelog: [v0.0.1...v0.0.2](https://github.com/adamsteele-sp/searchpilot-python/compare/v0.0.1...v0.0.2)

### Chores

* update SDK settings ([d461dd1](https://github.com/adamsteele-sp/searchpilot-python/commit/d461dd15151e63436180b217010030752c8c50ab))
