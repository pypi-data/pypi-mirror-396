from amptek_controller import AmptekDevice
from utils import Hdf5Handler
import numpy as np
import h5py
import matplotlib.pyplot as plt
import configparser
import time
from nanomax_controller import NanoMaxController

def cube_scan_meshgrid(hdf5_filepath, bounds:tuple, dwell_time, roi_energy, step_size_um:int):
    """Start a cube scan around the given center"""


    config = configparser.ConfigParser()
    config_filepath = r"C:\Users\CXRF\Code\depthpaint-c-xrf-interface\corapp\configurations\main_config.cfg"
    config.read(config_filepath)

    cxrf_controller =  AmptekDevice(config, maxrf_device=False)
    cxrf_controller.start_connection()
    cxrf_controller.set_calibration(-0.017286111111104674, 0.030652777777777862, 0, 1)
    nanomax_controller = NanoMaxController(config)
    nanomax_controller.start_connection()

    cxrf_controller.enable_mca_mcs()
    time.sleep(0.1)

    # Define the starting meshgrid
    a = int((bounds[0][1] - bounds[0][0])*1000 // step_size_um)
    b = int((bounds[1][1] - bounds[1][0])*1000 // step_size_um)
    c = 10
    print(f'{a}x{b}x{c} = {a*b*c} points to scan')
    x_start = np.linspace(bounds[0][0], bounds[0][1], num=a)
    y_start = np.linspace(bounds[1][0], bounds[1][1], num=b)
    z_start = np.linspace(bounds[2][0], bounds[2][1], num=c)
    points = np.array(np.meshgrid(x_start, y_start, z_start)).T.reshape(-1, 3).tolist()

    print(f'Starting cube scan with {len(points)} points')

    data_cube = np.zeros((a, b, c), dtype=np.int32)

    step_x_mm = round((bounds[0][1] - bounds[0][0]) / a, 3)
    step_y_mm = round((bounds[1][1] - bounds[1][0]) / b, 3)
    step_z_mm = round((bounds[2][1] - bounds[2][0]) / c, 3)
    print(f'{bounds=} {step_x_mm=}, {step_y_mm=}, {step_z_mm=}')

    count = 0
    for point in points:
        count += 1
        x, y, z = point
        x = round(x, 3)
        y = round(y, 3)
        z = round(z, 3)
        nanomax_controller.move_to("x", x)
        nanomax_controller.move_to("y", y)
        nanomax_controller.move_to("z", z)
        _, int_spectrum, _ = cxrf_controller.get_spectrum(get_status=False, clear_spectrum=True)
        time.sleep(dwell_time / 1000)
        _, int_spectrum, _ = cxrf_controller.get_spectrum(get_status=False, clear_spectrum=True, energy_roi=roi_energy)
        sum_spectrum = sum(int_spectrum)
        x_index = int((x - bounds[0][0]) / step_x_mm)
        y_index = int((y - bounds[1][0]) / step_y_mm)
        z_index = int((z - bounds[2][0]) / step_z_mm)
        if x_index >= data_cube.shape[0] :
            x_index = data_cube.shape[0] - 1
        if y_index >= data_cube.shape[1] :
            y_index = data_cube.shape[1] - 1
        if z_index >= data_cube.shape[2] :
            z_index = data_cube.shape[2] - 1
        print(f'Point scanned ({count}/{len(points)}) : {(x, y, z)}, sum_spectrum : {sum_spectrum}, stored at index : {x_index, y_index, z_index}')
        data_cube[x_index, y_index, z_index] = sum_spectrum

        Hdf5Handler.save_data_to_hdf5(hdf5_filepath, data_cube, np.array([0,1,0]), project_name="Test confocal alignment")

    # visualize_3d_mapping(hdf5_filepath)
    cxrf_controller.disable_mca_mcs()
    cxrf_controller.stop_connection()
    return data_cube

def visualize_3d_mapping(hdf5_filepath):
    with h5py.File(hdf5_filepath, 'r') as hdf5_file:
        data_cube = hdf5_file.get("/Test confocal alignment/Object/XRF_Analysis/C-XRF Profile")
        if data_cube is None :
            raise ValueError(f"Could not find dataset inside hdf5file : {hdf5_filepath}")
        

        x = list(np.arange(0, data_cube.shape[0])) * data_cube.shape[1] * data_cube.shape[2]
        x.sort()
        y = list(np.arange(0, data_cube.shape[1])) * data_cube.shape[2] 
        y.sort()
        y = y * data_cube.shape[0]
        z = list(np.arange(0, data_cube.shape[2]))
        z.sort()
        z = z * data_cube.shape[1] * data_cube.shape[0]
        c = data_cube[:, :, :]

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        scatter = ax.scatter(x,y,z,c=c)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')

        # produce a legend with the unique colors from the scatter
        legend1 = ax.legend(*scatter.legend_elements(),
                            loc='lower left', title="Values")
        ax.add_artist(legend1)

        plt.show()

if __name__ == "__main__":

    # DEFINE HDF5 FILEPATH TO SAVE CUBE SCAN DATA
    hdf5_filepath=r"C:\Users\CXRF\Desktop\test_confocal_cube_scan_6.hdf5"
    
    # UNCOMMENT TO RUN CUBE SCAN
    # cube_scan_meshgrid(hdf5_filepath=hdf5_filepath,
    #                     bounds=((3.46, 3.56), (4.34, 4.46), (0.300, 1.30)),
    #                     dwell_time=1000,
    #                     roi_energy=(7.9, 9.0),
    #                     step_size_um=10)
    
    # UNCOMMENT TO VISUALIZE CUBE SCAN DATA
    visualize_3d_mapping(hdf5_filepath)