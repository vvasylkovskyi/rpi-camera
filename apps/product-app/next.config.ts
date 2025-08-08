import type { NextConfig } from "next";
import withModuleFederation from "@module-federation/nextjs-mf"

const nextConfig: NextConfig = new withModuleFederation({
  name: 'product',
  filename: 'static/chunks/remoteEntry.js',
  exposes: {
    './ProductApp': './src/app/layout.tsx', // expose the root layout
  },
  shared: {
    react: { singleton: true },
    'react-dom': { singleton: true },
  },
  extraOptions: {
  },
});

nextConfig.output = 'standalone';

export default nextConfig;
  