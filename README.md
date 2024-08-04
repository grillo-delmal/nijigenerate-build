# NijiGenerate builder

This is my reference building process for nijigenerate and nijiexpose. 
I built this with the purpose of using it as reference to eventually package 
the software into COPR.

## Dependencies

You just need podman to run this, should work fine with Docker too with some tweaks.

Remember to initalize the repository submodules before continuing

```sh
git submodule update --init --recursive
```

## Build

Just run the deploy script

```sh
./deploy.sh
```

The result should end up in the `build_out/nijigenerate` and `build_out/nijiexpose` 
folders. It will also create some other artifacts inside the `build_out` directory 
and a `cache` directory, you can ignore/delete those if you want.

## Run

Go into the `build_out/nijigenerate` folder and run the `./nijigenerate` binary 
or use the `run-creator.sh` script.

The same is applicable for nijiexpose.

## Debug

If you want to run a debug version of the application, run the `deploy.sh` 
and `run.sh` scripts with the `DEBUG=1` env variable.

```sh
DEBUG=1 ./deploy.sh
DEBUG=1 ./run-nijigenerate.sh
# or
DEBUG=1 ./run-nijiexpose.sh
```

There are some other variables you can toy with inside the deploy.sh file ...
might convert them to params, but not interested in doing that gruntwork right now.