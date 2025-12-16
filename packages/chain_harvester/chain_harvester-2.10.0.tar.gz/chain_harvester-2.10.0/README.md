# Chain Harvester

Chain Harvester is a utility for seamlessly interacting with Ethereum-like blockchains. It provides a comprehensive set of methods to fetch information from the blockchain, including blocks, events, and storage content of contracts.

- **Github repository**: <https://github.com/blockanalitica/chain-harvester/>

## Features

- **Web3 Integration**: Direct integration with the Web3.py library for querying Ethereum nodes.
- **Event Decoding**: Decode event logs and get events for specific contracts or topics.
- **Contract Storage**: Fetch storage content at specific positions for a contract.
- **Multicall Support**: Batch multiple contract calls into a single request.
- **Retry Mechanism**: Built-in retry mechanism for HTTP requests.
- **ABI Management**: Load and cache ABI (Application Binary Interface) data for contracts.


## Notes

- **This should never be used to work with blockchain. Only for fetching data, not for doing transactions or equivalent.** The reason why is because of the retry logic on the chain itself. We're retrying POST requests which meas it could create multiple transactions or other action in case the request fails.

## Installation

To install Chain Harvester, simply use `pip`:

```
pip install chain-harvester
```

Make sure you have `pip` installed and are using a version of Python that is compatible with Chain Harvester.

## Supported Chains

Chain Harvester provides specific implementations for different blockchains and their respective versions or networks. Each chain is encapsulated in its own class, which inherits from the base `Chain` class. These chain-specific classes contain data and methods that are relevant to their respective blockchains.

### Ethereum Chains

- **Ethereum Mainnet**: Located in `networks.ethereum.mainnet`. This class, `EthereumMainnetChain`, interacts with the Ethereum mainnet.
  
  ```python
  from networks.ethereum.mainnet import EthereumMainnetChain
  
  eth_main = EthereumMainnetChain(rpc="YOUR_RPC_ENDPOINT")
  ```

### Gnosis Chains

- **Gnosis Mainnet**: Located in `networks.gnosis.mainnet`. This class is designed to interact with the Gnosis mainnet.

  ```python
  from networks.gnosis.mainnet import GnosisMainnetChain
  
  gnosis_main = GnosisMainnetChain(rpc="YOUR_RPC_ENDPOINT")
  ```


## Contributing

We welcome contributions from everyone! Here's how you can help:

1. **Fork and Clone**: Begin by forking the Chain Harvester repository to your GitHub account. Clone this forked repository to your local machine to start making changes.
2. **Set Up Environment**: Ensure you have the necessary dependencies installed. Follow the installation guide in the README to set up your environment.
3. **Make Changes**: Create a new branch for your changes. Make sure to write clean code and follow the project's coding standards. It's also a good practice to write tests for any new features or bug fixes.
4. **Commit and Push**: Once you've made your changes, commit them with a clear and descriptive commit message. Push your changes to your forked repository on GitHub.
5. **Submit a Pull Request (PR)**: Go to the Chain Harvester repository on GitHub and create a new pull request. Make sure to provide a detailed description of your changes. This will help the maintainers review your PR more efficiently.
6. **Review**: Maintainers and contributors will review your PR. They might suggest changes or improvements. Make sure to address any comments or feedback.
7. **Merge**: Once your PR is approved, it will be merged into the main codebase. Congratulations, and thank you for your contribution!

For any questions or discussions, please open an issue or join our community chat.

## Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for our commit messages. This leads to more readable messages that are easy to follow when looking through the project history.

### Format

Each commit message consists of a **header**, a **body**, and a **footer**. The header has a special format that includes a **type**, an optional **scope**, and a **description**:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

For example:

```
fix(server): fix crash on start-up

The application crashed on start-up due to an environment variable missing. This commit ensures that the application checks for the environment variable before start-up.
```

### Types

We primarily use the following commit types:

- **fix**: Patches a bug in your codebase.
- **feat**: Introduces a new feature to the codebase.
- **BREAKING CHANGE**: An API change that breaks backward compatibility.
- **chore**: Regular code maintenance.
- **docs**: Documentation only changes.
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc).
- **refactor**: A code change that neither fixes a bug nor adds a feature.
- **perf**: A code change that improves performance.
- **test**: Adding missing tests or correcting existing ones.

For more details, visit the [Conventional Commits website](https://www.conventionalcommits.org/).

