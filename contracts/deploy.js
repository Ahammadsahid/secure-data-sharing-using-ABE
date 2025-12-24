// Hardhat/Ethers.js deployment script for KeyAuthority contract
async function main() {
  console.log("Starting KeyAuthority deployment...");

  // Get signer (connected account)
  const [deployer] = await ethers.getSigners();
  console.log(`Deploying with account: ${deployer.address}`);

  // Define authorities - using your Ganache accounts
  const authorities = [
    "0x8d4d6c34EDEA4E1eb2fc2423D6A091cdCB34DB48",
    "0xfbe684383F81045249eB1E5974415f484E6F9f21",
    "0xd2A2E096ef8313db712DFaB39F40229F17Fd3f94",
    "0x57D14fF746d33127a90d4B888D378487e2C69f1f",
    "0x0e852C955e5DBF7187Ec6ed7A3B131165C63cf9a",
    "0x211Db7b2b475E9282B31Bd0fF39220805505Ff71",
    "0x7FAdEAa4442bc60678ee16E401Ed80342aC24d16"
  ];
  
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
