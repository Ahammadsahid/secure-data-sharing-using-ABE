// Hardhat/Ethers.js deployment script for KeyAuthority contract
async function main() {
  console.log("Starting KeyAuthority deployment...");

  // Get signer (connected account)
  const [deployer] = await ethers.getSigners();
  console.log(`Deploying with account: ${deployer.address}`);

  // Define authorities - default: first 7 unlocked accounts from the current provider
  // Optional override via env var GANACHE_AUTHORITIES (JSON array or comma-separated list)
  const rawAuthorities = process.env.GANACHE_AUTHORITIES || process.env.AUTHORITIES;
  let authorities;
  if (rawAuthorities) {
    const trimmed = rawAuthorities.trim();
    authorities = trimmed.startsWith("[")
      ? JSON.parse(trimmed)
      : trimmed.split(",").map((s) => s.trim()).filter(Boolean);
  } else {
    const signers = await ethers.getSigners();
    authorities = signers.slice(0, 7).map((s) => s.address);
  }
  
  const threshold = 4;

  // Deploy contract
  const KeyAuthority = await ethers.getContractFactory("KeyAuthority");
  const contract = await KeyAuthority.deploy(authorities, threshold, {
    gasLimit: 5000000, // Increased gas limit
    gasPrice: ethers.utils.parseUnits("2", "gwei")
  });

  await contract.deployed();

  console.log("✓ KeyAuthority deployed to:", contract.address);
  console.log("✓ Owner:", deployer.address);
  console.log("✓ Threshold:", threshold);
  console.log("✓ Authorities count:", authorities.length);

  // Save deployment info
  const fs = require("fs");
  const deploymentInfo = {
    contractAddress: contract.address,
    owner: deployer.address,
    threshold: threshold,
    authorities: authorities,
    network: hre.network.name,
    deploymentBlock: await ethers.provider.getBlockNumber()
  };

  fs.writeFileSync(
    "../backend/blockchain/DEPLOYMENT_INFO.json",
    JSON.stringify(deploymentInfo, null, 2)
  );

  console.log("✓ Deployment info saved to DEPLOYMENT_INFO.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
