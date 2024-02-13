# rock-paper-scissors
global game of rock paper scissors on farcaster

the backend is written in flask and deployed on vercel, the frontend is rendered via farcaster frames

## development

setup a conda (or other virtual) environment
```
conda env update -f environment.yml
conda activate rock-paper-scissors
```

setup vercel
```
npm install vercel
```

run local app
```
npx vercel dev
```
