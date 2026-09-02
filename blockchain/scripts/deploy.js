import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { ethers } from "ethers";
import hre from "hardhat";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  const networkName = hre.globalOptions.network || "anvil";
  const rpcUrl =
    hre.userConfig.networks?.[networkName]?.url ||
    process.env.BLOCKCHAIN_RPC_URL ||
    "http://127.0.0.1:8545";
  const chainId =
    hre.userConfig.networks?.[networkName]?.chainId ||
    31337;

  console.log(`Connecting to network: ${networkName} (${rpcUrl})...`);

  // Initialize provider and deployer signer
  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const signer = await provider.getSigner(0);
  const deployerAddress = await signer.getAddress();

  console.log(`Deployer address: ${deployerAddress}`);

  // Read the compiled contract artifact
  const artifact = await hre.artifacts.readArtifact("CyberGraphAudit");

  // Create contract factory and send deployment transaction
  const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, signer);
  const contract = await factory.deploy();

  const deploymentTx = contract.deploymentTransaction();
  const txHash = deploymentTx ? deploymentTx.hash : "N/A";

  console.log(`Deployment transaction submitted: ${txHash}`);

  // Wait for the transaction to be mined
  await contract.waitForDeployment();
  const contractAddress = await contract.getAddress();

  // Print required deployment details
  console.log("================ Deployment Summary ================");
  console.log(`Network Name:              ${networkName}`);
  console.log(`Deployer Address:          ${deployerAddress}`);
  console.log(`Deployed Contract Address: ${contractAddress}`);
  console.log(`Transaction Hash:          ${txHash}`);
  console.log("====================================================");

  // Ensure deployments directory exists
  const deploymentsDir = path.resolve(__dirname, "../deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  // Save deployment metadata (excluding any sensitive keys)
  const deploymentData = {
    network: networkName,
    chainId: Number(chainId),
    contractName: "CyberGraphAudit",
    contractAddress: contractAddress,
    deployerAddress: deployerAddress,
    transactionHash: txHash,
  };

  const deploymentFilePath = path.join(deploymentsDir, "deployment.json");
  fs.writeFileSync(
    deploymentFilePath,
    JSON.stringify(deploymentData, null, 2),
    "utf-8"
  );
  console.log(`Deployment details saved to: ${deploymentFilePath}`);

  // Also save the ABI for downstream Web3 / client usage
  const abiDir = path.resolve(__dirname, "../abi");
  if (!fs.existsSync(abiDir)) {
    fs.mkdirSync(abiDir, { recursive: true });
  }
  const abiFilePath = path.join(abiDir, "CyberGraphAudit.json");
  fs.writeFileSync(
    abiFilePath,
    JSON.stringify(artifact.abi, null, 2),
    "utf-8"
  );
  console.log(`ABI exported to: ${abiFilePath}`);
}

main().catch((error) => {
  console.error("Deployment failed:", error);
  process.exitCode = 1;
});
