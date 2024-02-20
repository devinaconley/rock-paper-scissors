# rock-paper-scissors
global game of rock paper scissors on farcaster

the backend is written in flask and deployed on vercel, the frontend is rendered via farcaster frames

## setup

setup a conda (or other virtual) environment
```
conda env update -f environment.yml
conda activate rock-paper-scissors
```

setup vercel
```
npm install vercel
```


## development

run unit tests
```
pytest -v -s
```

run local app
```
npx vercel dev
```

you can run the frame debugger provided by [frames.js](https://github.com/framesjs/frames.js) to test locally


## deployment

_TODO_
