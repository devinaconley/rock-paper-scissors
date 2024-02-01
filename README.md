# rock-paper-scissors
global game of rock paper scissors on farcaster

the backend is written in flask and deployed on vercel, the frontend is rendered via farcaster frames

## development

setup a conda (or other virtual) environment
```
conda create -n rock-paper-scissors python=3.11
conda activate rock-paper-scissors
pip install -r requirements
```

setup vercel
```
npm install vercel
```

run local app
```
npx vercel dev
```
