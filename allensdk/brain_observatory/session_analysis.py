# Copyright 2016 Allen Institute for Brain Science
# This file is part of Allen SDK.
#
# Allen SDK is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Allen SDK is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Allen SDK.  If not, see <http://www.gnu.org/licenses/>.

from .static_gratings import StaticGratings
from .locally_sparse_noise import LocallySparseNoise
from .natural_scenes import NaturalScenes
from .drifting_gratings import DriftingGratings
from .natural_movie import NaturalMovie
import six
from allensdk.core.brain_observatory_nwb_data_set \
    import BrainObservatoryNwbDataSet
from . import stimulus_info
from allensdk.brain_observatory.brain_observatory_exceptions \
    import BrainObservatoryAnalysisException
from . import brain_observatory_plotting as cp
import argparse
import logging
import os



def multi_dataframe_merge(dfs):
    out_df = None
    for _, df in enumerate(dfs):
        if out_df is None:
            out_df = df
        else:
            out_df = out_df.merge(df, left_index=True,
                                  right_index=True, suffixes=['', '_deleteme'])

    bad_columns = set([c for c in out_df.columns if c.endswith('deleteme')])
    out_df.drop(list(bad_columns), axis=1, inplace=True)

    return out_df


class SessionAnalysis(object):
    _log = logging.getLogger('allensdk.brain_observatory.session_analysis')

    def __init__(self, nwb_path, save_path):
        self.nwb = BrainObservatoryNwbDataSet(nwb_path)
        self.save_path = save_path
        self.save_dir = os.path.dirname(save_path)

        self.metrics_a = {}
        self.metrics_b = {}
        self.metrics_c = {}

        self.metadata = self.nwb.get_metadata()

    def append_metadata(self, df):
        for k, v in six.iteritems(self.metadata):
            df[k] = v

    def save_session_a(self, dg, nm1, nm3, peak):
        nwb = BrainObservatoryNwbDataSet(self.save_path)
        nwb.save_analysis_dataframes(
            ('stim_table_dg', dg.stim_table),
            ('sweep_response_dg', dg.sweep_response),
            ('mean_sweep_response_dg', dg.mean_sweep_response),
            ('peak', peak),
            ('sweep_response_nm1', nm1.sweep_response),
            ('stim_table_nm1', nm1.stim_table),
            ('sweep_response_nm3', nm3.sweep_response))

        nwb.save_analysis_arrays(
            ('response_dg', dg.response),
            ('binned_cells_sp', nm1.binned_cells_sp),
            ('binned_cells_vis', nm1.binned_cells_vis),
            ('binned_dx_sp', nm1.binned_dx_sp),
            ('binned_dx_vis', nm1.binned_dx_vis),
            ('noise_corr_dg', dg.noise_correlation),
            ('signal_corr_dg', dg.signal_correlation),
            ('rep_similarity_dg', dg.representational_similarity)
            )


    def save_session_b(self, sg, nm1, ns, peak):
        nwb = BrainObservatoryNwbDataSet(self.save_path)
        nwb.save_analysis_dataframes(
            ('stim_table_sg', sg.stim_table),
            ('sweep_response_sg', sg.sweep_response),
            ('mean_sweep_response_sg', sg.mean_sweep_response),
            ('sweep_response_nm1', nm1.sweep_response),
            ('stim_table_nm1', nm1.stim_table),
            ('sweep_response_ns', ns.sweep_response),
            ('stim_table_ns', ns.stim_table),
            ('mean_sweep_response_ns', ns.mean_sweep_response),
            ('peak', peak))

        nwb.save_analysis_arrays(
            ('response_sg', sg.response),
            ('response_ns', ns.response),
            ('binned_cells_sp', nm1.binned_cells_sp),
            ('binned_cells_vis', nm1.binned_cells_vis),
            ('binned_dx_sp', nm1.binned_dx_sp),
            ('binned_dx_vis', nm1.binned_dx_vis),
            ('noise_corr_sg', sg.noise_correlation),
            ('signal_corr_sg', sg.signal_correlation),
            ('rep_similarity_sg', sg.representational_similarity),
            ('noise_corr_ns', ns.noise_correlation),
            ('signal_corr_ns', ns.signal_correlation),
            ('rep_similarity_ns', ns.representational_similarity)
            )

    def save_session_c(self, lsn, nm1, nm2, peak):
        nwb = BrainObservatoryNwbDataSet(self.save_path)
        nwb.save_analysis_dataframes(
            ('stim_table_lsn', lsn.stim_table),
            ('sweep_response_nm1', nm1.sweep_response),
            ('peak', peak),
            ('sweep_response_nm2', nm2.sweep_response),
            ('sweep_response_lsn', lsn.sweep_response),
            ('mean_sweep_response_lsn', lsn.mean_sweep_response))

        nwb.save_analysis_arrays(
            ('receptive_field_lsn', lsn.receptive_field),
            ('mean_response_lsn', lsn.mean_response),
            ('celltraces_dff', nm1.dfftraces),
            ('binned_dx_sp', nm1.binned_dx_sp),
            ('binned_dx_vis', nm1.binned_dx_vis),
            ('binned_cells_sp', nm1.binned_cells_sp),
            ('binned_cells_vis', nm1.binned_cells_vis))

        LocallySparseNoise.save_cell_index_receptive_field_analysis_dict(lsn.cell_index_receptive_field_analysis_data_dict, nwb, stimulus_info.LOCALLY_SPARSE_NOISE)

    def save_session_c2(self, lsn4, lsn8, nm1, nm2, peak):
        nwb = BrainObservatoryNwbDataSet(self.save_path)
        nwb.save_analysis_dataframes(
            ('stim_table_lsn4', lsn4.stim_table),
            ('stim_table_lsn8', lsn8.stim_table),
            ('sweep_response_nm1', nm1.sweep_response),
            ('peak', peak),
            ('sweep_response_nm2', nm2.sweep_response),
            ('sweep_response_lsn4', lsn4.sweep_response),
            ('sweep_response_lsn8', lsn8.sweep_response),
            ('mean_sweep_response_lsn4', lsn4.mean_sweep_response),
            ('mean_sweep_response_lsn8', lsn8.mean_sweep_response))

        merge_mean_response = LocallySparseNoise.merge_mean_response(
            lsn4.mean_response,
            lsn8.mean_response)

        nwb.save_analysis_arrays(
            ('mean_response_lsn4', lsn4.mean_response),
            ('mean_response_lsn8', lsn8.mean_response),
            ('receptive_field_lsn4', lsn4.receptive_field),
            ('receptive_field_lsn8', lsn8.receptive_field),
            ('merge_mean_response', merge_mean_response),
            ('celltraces_dff', nm1.dfftraces),
            ('binned_dx_sp', nm1.binned_dx_sp),
            ('binned_dx_vis', nm1.binned_dx_vis),
            ('binned_cells_sp', nm1.binned_cells_sp),
            ('binned_cells_vis', nm1.binned_cells_vis))

        LocallySparseNoise.save_cell_index_receptive_field_analysis_dict(lsn4.cell_index_receptive_field_analysis_data_dict, nwb, stimulus_info.LOCALLY_SPARSE_NOISE_4DEG)
        LocallySparseNoise.save_cell_index_receptive_field_analysis_dict(lsn8.cell_index_receptive_field_analysis_data_dict, nwb, stimulus_info.LOCALLY_SPARSE_NOISE_8DEG)

    def append_metrics_drifting_grating(self, metrics, dg):
        metrics["osi_dg"] = dg.peak["osi_dg"]
        metrics["dsi_dg"] = dg.peak["dsi_dg"]
        metrics["pref_dir_dg"] = [dg.orivals[i]
                                  for i in dg.peak["ori_dg"].values]
        metrics["pref_tf_dg"] = [dg.tfvals[i] for i in dg.peak["tf_dg"].values]
        metrics["p_dg"] = dg.peak["ptest_dg"]
        metrics["cv_os_dg"] = dg.peak["cv_os_dg"]
        metrics["cv_ds_dg"] = dg.peak["cv_ds_dg"]
        metrics["reliability_dg"] = dg.peak["reliability_dg"]
        metrics["tfdi_dg"] = dg.peak["tf_index_dg"]
        metrics["run_mod_dg"] = dg.peak["run_modulation_dg"]
        metrics["p_run_mod_dg"] = dg.peak["p_run_dg"]
        metrics["peak_dff_dg"] = dg.peak["peak_dff_dg"]


    def append_metrics_static_grating(self, metrics, sg):
        metrics["osi_sg"] = sg.peak["osi_sg"]
        metrics["pref_ori_sg"] = [sg.orivals[i]
                                  for i in sg.peak["ori_sg"].values]
        metrics["pref_sf_sg"] = [sg.sfvals[i] for i in sg.peak["sf_sg"].values]
        metrics["pref_phase_sg"] = [sg.phasevals[i]
                                    for i in sg.peak["phase_sg"].values]
        metrics["p_sg"] = sg.peak["ptest_sg"]
        metrics["time_to_peak_sg"] = sg.peak["time_to_peak_sg"]
        metrics["run_mod_sg"] = sg.peak["run_modulation_sg"]
        metrics["p_run_mod_sg"] = sg.peak["p_run_sg"]
        metrics["cv_os_sg"] = sg.peak["cv_os_sg"]

    def append_metrics_natural_scene(self, metrics, ns):
        metrics["pref_image_ns"] = ns.peak["scene_ns"]
        metrics["p_ns"] = ns.peak["ptest_ns"]
        metrics["time_to_peak_ns"] = ns.peak["time_to_peak_ns"]
        metrics["image_sel_ns"] = ns.peak["image_selectivity_ns"]
        metrics["reliability_ns"] = ns.peak["reliability_ns"]
        metrics["run_mod_ns"] = ns.peak["run_modulation_ns"]
        metrics["p_run_mod_ns"] = ns.peak["p_run_ns"]
        metrics["peak_dff_ns"] = ns.peak["peak_dff_ns"]

    def append_metrics_locally_sparse_noise(self, metrics, lsn):
        metrics['rf_chi2_lsn'] = lsn.peak['chi_squared_analysis/min_p']
        metrics['rf_area_on_lsn'] = lsn.peak['rf_area_on_lsn']
        metrics['rf_center_on_x_lsn'] = lsn.peak['rf_center_on_x_lsn']
        metrics['rf_center_on_y_lsn'] = lsn.peak['rf_center_on_y_lsn']
        metrics['rf_area_off_lsn'] = lsn.peak['rf_area_off_lsn']
        metrics['rf_center_off_x_lsn'] = lsn.peak['rf_center_off_x_lsn']
        metrics['rf_center_off_y_lsn'] = lsn.peak['rf_center_off_y_lsn']
        metrics['rf_distance_lsn'] = lsn.peak['rf_distance_lsn']
        metrics['rf_overlap_index_lsn'] = lsn.peak['rf_overlap_index_lsn']

    def verify_roi_lists_equal(self, roi1, roi2):
        if len(roi1) != len(roi2):
            raise BrainObservatoryAnalysisException(
                "Error -- ROI lists are of different length")
        for i in range(len(roi1)):
            if roi1[i] != roi2[i]:
                raise BrainObservatoryAnalysisException(
                    "Error -- ROI lists have different entries")

    def session_a(self, plot_flag=False, save_flag=True):
        nm1 = NaturalMovie(self.nwb, 'natural_movie_one')
        nm3 = NaturalMovie(self.nwb, 'natural_movie_three')
        dg = DriftingGratings(self.nwb)

        dg.noise_correlation, _, _, _ = dg.get_noise_correlation()
        dg.signal_correlation, _ = dg.get_signal_correlation()
        dg.representational_similarity, _ = dg.get_representational_similarity()

        SessionAnalysis._log.info("Session A analyzed")
        peak = multi_dataframe_merge(
            [nm1.peak_run, dg.peak, nm1.peak, nm3.peak])

        self.append_metrics_drifting_grating(self.metrics_a, dg)
        self.metrics_a["roi_id"] = dg.roi_id

        self.append_metadata(peak)

        if save_flag:
            self.save_session_a(dg, nm1, nm3, peak)

        if plot_flag:
            cp._plot_3sa(dg, nm1, nm3, self.save_dir)
            cp.plot_drifting_grating_traces(dg, self.save_dir)

    def session_b(self, plot_flag=False, save_flag=True):
        ns = NaturalScenes(self.nwb)
        sg = StaticGratings(self.nwb)
        nm1 = NaturalMovie(self.nwb, 'natural_movie_one')
        SessionAnalysis._log.info("Session B analyzed")
        peak = multi_dataframe_merge(
            [nm1.peak_run, sg.peak, ns.peak, nm1.peak])
        self.append_metadata(peak)

        self.append_metrics_static_grating(self.metrics_b, sg)
        self.append_metrics_natural_scene(self.metrics_b, ns)
        self.verify_roi_lists_equal(sg.roi_id, ns.roi_id)
        self.metrics_b["roi_id"] = sg.roi_id

        sg.noise_correlation, _, _, _ = sg.get_noise_correlation()
        sg.signal_correlation, _ = sg.get_signal_correlation()
        sg.representational_similarity, _ = sg.get_representational_similarity()

        ns.noise_correlation, _ = ns.get_noise_correlation()
        ns.signal_correlation, _ = ns.get_signal_correlation()
        ns.representational_similarity, _ = ns.get_representational_similarity()

        if save_flag:
            self.save_session_b(sg, nm1, ns, peak)

        if plot_flag:
            cp._plot_3sb(sg, nm1, ns, self.save_dir)
            cp.plot_ns_traces(ns, self.save_dir)
            cp.plot_sg_traces(sg, self.save_dir)

    def session_c(self, plot_flag=False, save_flag=True):

        lsn = LocallySparseNoise(self.nwb, stimulus_info.LOCALLY_SPARSE_NOISE)
        nm2 = NaturalMovie(self.nwb, 'natural_movie_two')
        nm1 = NaturalMovie(self.nwb, 'natural_movie_one')
        SessionAnalysis._log.info("Session C analyzed")
        peak = multi_dataframe_merge([nm1.peak_run, nm1.peak, nm2.peak, lsn.peak])
        self.append_metadata(peak)

        self.append_metrics_locally_sparse_noise(self.metrics_c, lsn)
        self.metrics_c["roi_id"] = nm1.roi_id

        if save_flag:
            self.save_session_c(lsn, nm1, nm2, peak)

        if plot_flag:
            cp._plot_3sc(lsn, nm1, nm2, self.save_dir)
            cp.plot_lsn_traces(lsn, self.save_dir)

    def session_c2(self, plot_flag=False, save_flag=True):

        lsn4 = LocallySparseNoise(self.nwb, stimulus_info.LOCALLY_SPARSE_NOISE_4DEG)
        lsn8 = LocallySparseNoise(self.nwb, stimulus_info.LOCALLY_SPARSE_NOISE_8DEG)

        nm2 = NaturalMovie(self.nwb, 'natural_movie_two')
        nm1 = NaturalMovie(self.nwb, 'natural_movie_one')
        SessionAnalysis._log.info("Session C2 analyzed")
        peak = multi_dataframe_merge([nm1.peak_run, nm1.peak, nm2.peak, lsn.peak])
        self.append_metadata(peak)

        self.append_metrics_locally_sparse_noise(self.metrics_c, lsn)
        self.metrics_c["roi_id"] = nm1.roi_id

        if save_flag:
            self.save_session_c2(lsn4, lsn8, nm1, nm2, peak)

        if plot_flag:
            cp._plot_3sc(lsn4, nm1, nm2, self.save_dir, '_4deg')
            cp._plot_3sc(lsn8, nm1, nm2, self.save_dir, '_8deg')
            cp.plot_lsn_traces(lsn4, self.save_dir, '_4deg')
            cp.plot_lsn_traces(lsn4, self.save_dir, '_8deg')


def run_session_analysis(nwb_path, save_path, plot_flag=False, save_flag=True):
    save_dir = os.path.abspath(os.path.dirname(save_path))

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    session_analysis = SessionAnalysis(nwb_path, save_path)

    session = session_analysis.nwb.get_session_type()

    if session == stimulus_info.THREE_SESSION_A:
        session_analysis.session_a(plot_flag=plot_flag, save_flag=save_flag)
        metrics = session_analysis.metrics_a
    elif session == stimulus_info.THREE_SESSION_B:
        session_analysis.session_b(plot_flag=plot_flag, save_flag=save_flag)
        metrics = session_analysis.metrics_b
    elif session == stimulus_info.THREE_SESSION_C:
        session_analysis.session_c(plot_flag=plot_flag, save_flag=save_flag)
        metrics = session_analysis.metrics_c
    elif session == stimulus_info.THREE_SESSION_C2:
        session_analysis.session_c2(plot_flag=plot_flag, save_flag=save_flag)
        metrics = session_analysis.metrics_c
    else:
        raise IndexError("Unknown session: %s" % session)

    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_nwb")
    parser.add_argument("output_h5")

    parser.add_argument("--plot", action='store_true')

    args = parser.parse_args()
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    run_session_analysis(args.input_nwb, args.output_h5, args.plot)


if __name__ == '__main__':
    main()
