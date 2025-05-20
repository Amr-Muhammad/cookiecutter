import { config as dotenvConfig } from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
export const __dirname = path.dirname(__filename);
export const getFile = (location: string) => {
    return path.join(__dirname, location);
};

const envPath = getFile("../.env.test");
dotenvConfig({ path: envPath });
export const config = {
    baseURL: process.env.BASE_URL,
};
