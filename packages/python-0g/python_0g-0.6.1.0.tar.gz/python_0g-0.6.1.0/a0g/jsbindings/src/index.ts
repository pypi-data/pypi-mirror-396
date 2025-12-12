import {ethers} from "ethers";
import {createZGComputeNetworkBroker} from "@0glabs/0g-serving-broker";
// Import TypeChain factories from our bypass file

import {
  InferenceServing__factory,
  LedgerManager__factory,
  FineTuningServing__factory
} from "./typechain/factories";


export async function getOpenAIHeadersDemo(privateKey: string, query: string, providerAddress: string,  rpcUrl: string) {
    try {
        const provider = new ethers.JsonRpcProvider(rpcUrl);
        const wallet = new ethers.Wallet(privateKey, provider);
        const broker = await createZGComputeNetworkBroker(wallet);
        try {
            await broker.inference.acknowledgeProviderSigner(providerAddress);
        } catch (error: any) {
            if (!(error.message.includes('already acknowledged'))) {
                throw error;
            }
        }
        const {endpoint, model} = await broker.inference.getServiceMetadata(providerAddress);
        const headers = await broker.inference.getRequestHeaders(providerAddress, query);
        const requestHeaders: Record<string, string> = {};
        Object.entries(headers).forEach(([key, value]) => {
            if (typeof value === 'string') {
                requestHeaders[key] = value;
            }
        });

        return JSON.stringify({
            success: true,
            headers: requestHeaders,
            endpoint: endpoint,
            model: model,
            query: query,
        })

    } catch (error: any) {
        console.error('Error:', error);
        return JSON.stringify({
            success: false,
        })
    }
}


export async function getAllServices(privateKey: string, rpcUrl: string) {
    try {
        const provider = new ethers.JsonRpcProvider(rpcUrl);
        const wallet = new ethers.Wallet(privateKey, provider);
        const broker = await createZGComputeNetworkBroker(wallet);
        const services = await broker.inference.listService()
        return JSON.stringify({
            success: true,
            services: services,
        }, (_, value) => typeof value === "bigint" ? value.toString() : value)

    } catch (error: any) {
        console.error('Error:', error);
        return JSON.stringify({
            success: false,
        })
    }
}


export async function getAccount(privateKey: string, rpcUrl: string, providerAddress: string) {
    try {
        const provider = new ethers.JsonRpcProvider(rpcUrl);
        const wallet = new ethers.Wallet(privateKey, provider);
        const broker = await createZGComputeNetworkBroker(wallet);
        const account = await broker.inference.getAccount(providerAddress)
        return JSON.stringify({
            success: true,
            account: account,
        }, (_, value) => typeof value === "bigint" ? value.toString() : value)

    } catch (error: any) {
        console.error('Error:', error);
        return JSON.stringify({
            success: false,
        })
    }
}


export async function getAbi() {
    try {
        return JSON.stringify({
            success: true,
            inference: InferenceServing__factory.abi,
            ledger: LedgerManager__factory.abi,
            finetuning: FineTuningServing__factory.abi
        }, (_, value) => typeof value === "bigint" ? value.toString() : value)

    } catch (error: any) {
        console.error('Error:', error);
        return JSON.stringify({
            success: false,
        })
    }
}
