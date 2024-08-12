import struct
import numpy as np
import matplotlib.pyplot as plt
from scipy import io  # Import scipy for .mat file support

class WfmReadError(Exception):
    """error for unexpected things"""
    pass

def read_wfm(target):
    """return sample data from target WFM file"""
    with open(target, 'rb') as f:
        hbytes = f.read(838)
        meta = decode_header(hbytes)
        if meta['byte_order'] != 0x0f0f:
            raise WfmReadError('big-endian not supported in this example')
        if meta['version'] != b':WFM#003':
            raise WfmReadError('only version 3 wfms supported in this example')
        if meta['imp_dim_count'] != 1:
            raise WfmReadError('imp dim count not 1')
        if meta['exp_dim_count'] != 1:
            raise WfmReadError('exp dim count not 1')
        if meta['record_type'] != 2:
            raise WfmReadError('not WFMDATA_VECTOR')
        if meta['exp_dim_1_type'] != 0:
            raise WfmReadError('not EXPLICIT_SAMPLE')
        if meta['time_base_1'] != 0:
            raise WfmReadError('not BASE_TIME')
        tfrac_array = np.zeros(meta['Frames'], dtype=np.double)
        tdatefrac_array = np.zeros(meta['Frames'], dtype=np.double)
        tdate_array = np.zeros(meta['Frames'], dtype=np.int32)
        tfrac_array[0] = meta['tfrac']
        tdatefrac_array[0] = meta['tdatefrac']
        tdate_array[0] = meta['tdate']
        if meta['fastframe'] == 1:
            WUSp = np.fromfile(f, dtype='i4,f8,f8,i4', count=(meta['Frames'] - 1))
            tfrac_array[1:] = WUSp['f1']
            tdatefrac_array[1:] = WUSp['f2']
            tdate_array[1:] = WUSp['f3']
        bin_wave = np.memmap(filename=f,
                             dtype=meta['dformat'],
                             mode='r',
                             offset=meta['curve_offset'],
                             shape=(meta['avilable_values'], meta['Frames']),
                             order='F')
    bin_wave = bin_wave[meta['pre_values']:meta['avilable_values'] - meta['post_values'], :]
    scaled_array = bin_wave * meta['vscale'] + meta['voffset']
    return scaled_array, meta['tstart'], meta['tscale'], tfrac_array, tdatefrac_array, tdate_array

def decode_header(header_bytes):
    """returns a dict of wfm metadata"""
    wfm_info = {}
    if len(header_bytes) != 838:
        raise WfmReadError('wfm header bytes not 838')
    wfm_info['byte_order'] = struct.unpack_from('H', header_bytes, offset=0)[0]
    wfm_info['version'] = struct.unpack_from('8s', header_bytes, offset=2)[0]
    wfm_info['imp_dim_count'] = struct.unpack_from('I', header_bytes, offset=114)[0]
    wfm_info['exp_dim_count'] = struct.unpack_from('I', header_bytes, offset=118)[0]
    wfm_info['record_type'] = struct.unpack_from('I', header_bytes, offset=122)[0]
    wfm_info['exp_dim_1_type'] = struct.unpack_from('I', header_bytes, offset=244)[0]
    wfm_info['time_base_1'] = struct.unpack_from('I', header_bytes, offset=768)[0]
    wfm_info['fastframe'] = struct.unpack_from('I', header_bytes, offset=78)[0]
    wfm_info['Frames'] = struct.unpack_from('I', header_bytes, offset=72)[0] + 1
    wfm_info['summary_frame'] = struct.unpack_from('h', header_bytes, offset=154)[0]
    wfm_info['curve_offset'] = struct.unpack_from('i', header_bytes, offset=16)[0]
    wfm_info['vscale'] = struct.unpack_from('d', header_bytes, offset=168)[0]
    wfm_info['voffset'] = struct.unpack_from('d', header_bytes, offset=176)[0]
    wfm_info['tstart'] = struct.unpack_from('d', header_bytes, offset=496)[0]
    wfm_info['tscale'] = struct.unpack_from('d', header_bytes, offset=488)[0]
    wfm_info['tfrac'] = struct.unpack_from('d', header_bytes, offset=788)[0]
    wfm_info['tdatefrac'] = struct.unpack_from('d', header_bytes, offset=796)[0]
    wfm_info['tdate'] = struct.unpack_from('I', header_bytes, offset=804)[0]
    dpre = struct.unpack_from('I', header_bytes, offset=822)[0]
    wfm_info['dpre'] = dpre
    dpost = struct.unpack_from('I', header_bytes, offset=826)[0]
    wfm_info['dpost'] = dpost
    readbytes = dpost - dpre
    wfm_info['readbytes'] = readbytes
    allbytes = struct.unpack_from('I', header_bytes, offset=830)[0]
    wfm_info['allbytes'] = allbytes
    code = struct.unpack_from('i', header_bytes, offset=240)[0]
    wfm_info['code'] = code
    bps = struct.unpack_from('b', header_bytes, offset=15)[0]
    wfm_info['bps'] = bps
    if code == 7 and bps == 1:
        dformat = 'int8'
        samples = readbytes
    elif code == 0 and bps == 2:
        dformat = 'int16'
        samples = readbytes // 2
    elif code == 4 and bps == 4:
        dformat = 'single'
        samples = readbytes // 4
    else:
        raise WfmReadError('data type code or bytes-per-sample not understood')
    wfm_info['dformat'] = dformat
    wfm_info['samples'] = samples
    wfm_info['avilable_values'] = allbytes // bps
    wfm_info['pre_values'] = dpre // bps
    wfm_info['post_values'] = (allbytes - dpost) // bps
    return wfm_info

if __name__ == "__main__":
    target_file = r"C:\Users\catnip\Downloads\Tek001\Tek001_ch8.wfm"

    try:
        scaled_array, tstart, tscale, tfrac_array, tdatefrac_array, tdate_array = read_wfm(target_file)

        # Save waveform data to .mat file
        mat_data = {
            'scaled_array': scaled_array,
            'tstart': tstart,
            'tscale': tscale,
            'tfrac_array': tfrac_array,
            'tdatefrac_array': tdatefrac_array,
            'tdate_array': tdate_array
        }
        io.savemat(r"C:\Users\catnip\Downloads\Tek001\Tek001_ch8.mat", mat_data)

        # Optional: Plotting example
        num_points = scaled_array.shape[0]
        time_values = np.linspace(tstart, tstart + num_points * tscale, num_points, endpoint=False)

        plt.figure(figsize=(10, 6))
        plt.plot(time_values, scaled_array, label='Waveform Data')
        plt.xlabel('Time')
        plt.ylabel('Voltage')
        plt.title('Voltage vs. Time')
        plt.grid(True)
        plt.legend()
        plt.show()

    except WfmReadError as e:
        print(f"Error reading {target_file}: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
