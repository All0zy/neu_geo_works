using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;

namespace PPPPrecisionPointPositioning
{
    public sealed class PppInputFiles
    {
        public string Sp3PrevPath;
        public string Sp3TodayPath;
        public string Sp3NextPath;
        public string ClkPath;
        public string AtxPath;
        public string ObsPath;

        public void Validate()
        {
            ValidateSingle(Sp3PrevPath, "SP3 前一天文件");
            ValidateSingle(Sp3TodayPath, "SP3 当天文件");
            ValidateSingle(Sp3NextPath, "SP3 后一天文件");
            ValidateSingle(ClkPath, "CLK 文件");
            ValidateSingle(AtxPath, "ATX 文件");
            ValidateSingle(ObsPath, "OBS 文件");
        }

        private static void ValidateSingle(string path, string displayName)
        {
            if (string.IsNullOrWhiteSpace(path))
                throw new InvalidOperationException("未选择" + displayName + "。");
            if (!File.Exists(path))
                throw new FileNotFoundException(displayName + "不存在: " + path);
        }
    }

    public enum PppReferenceMode
    {
        ConvergedMean = 0,
        RinexApprox = 1,
        ManualXyz = 2
    }

    public sealed class PppEvaluationOptions
    {
        public PppReferenceMode ReferenceMode = PppReferenceMode.ConvergedMean;
        public double[] ManualReferenceXyz = new double[3];
        public int StatisticsStartEpoch = -1;
    }

    public sealed class PppResult
    {
        public double TotalRms;
        public double NRms;
        public double ERms;
        public double URms;

        public double ScatterTotalRms;
        public double ScatterNRms;
        public double ScatterERms;
        public double ScatterURms;

        public double AbsoluteTotalRms;
        public double AbsoluteNRms;
        public double AbsoluteERms;
        public double AbsoluteURms;

        public bool HasAbsoluteReference;
        public string PrimaryMetricName;
        public string ReferenceMode;

        public double[] ReferenceXyz;
        public double[] ScatterReferenceXyz;
        public double[] AbsoluteReferenceXyz;

        public int UsedEpochCount;
        public int ConvergedEpochCount;
        public int StatisticsEpochCount;
        public int StatisticsStartEpoch;
        public string Summary;

        public PppResult()
        {
            ReferenceXyz = new double[3];
            ScatterReferenceXyz = new double[3];
            AbsoluteReferenceXyz = new double[3];
            PrimaryMetricName = "";
            ReferenceMode = "";
            Summary = "";
        }
    }

    public sealed class PppOptions
    {
        public bool UseGps = true;
        public bool UseGlonass = true;
        public bool UseGalileo = true;
        public bool UseBds = false;

        public int ClockIntervalSeconds = 30;
        public double ElevationCutoffDeg = 10.0;

        public bool PreferClockFile = true;
        public bool StaticMode = true;

        public double SigmaCodeMeters = 0.60;
        public double SigmaPhaseMeters = 0.008;
        public double InitialClockMeters = 100000.0;
        public double InitialZwdMeters = 0.30;
        public double InitialAmbMeters = 100.0;

        public double ProcessNoisePos2PerEpoch = 1e-8;
        public double ProcessNoiseClock2PerEpoch = 25.0;
        public double ProcessNoiseZwd2PerEpoch = 1e-6;
        public double ProcessNoiseAmb2PerEpoch = 1e-10;

        public int BurnInEpochs = 120;
        public int MinSatsPerEpoch = 4;
        public int MaxIterations = 8;

        public double SlipGeometryFreeThresholdMeters = 0.08;
        public double ResidualOutlierCodeMeters = 8.0;
        public double ResidualOutlierPhaseMeters = 0.10;

        public static PppOptions CreateDefault()
        {
            return new PppOptions();
        }
    }

    public static class PppConstants
    {
        public const int SatelliteCount = 105;
        public const double SpeedOfLight = 299792458.0;
        public const double OmegaEarth = 7.2921151467e-5;
        public const double Mu = 3.986005e14;
        public const double DegToRad = Math.PI / 180.0;
        public const double RadToDeg = 180.0 / Math.PI;
    }

    public sealed class FrequencyResult
    {
        public double[,] Freq = new double[106, 3];
        public double[,] Wavl = new double[106, 3];
    }

    public static class SatelliteFrequencies
    {
        public static FrequencyResult Get()
        {
            FrequencyResult r = new FrequencyResult();
            int[] glok = new int[] { 1, -4, 5, 6, 1, -4, 5, 6, -2, -7, 0, -1, -2, -7, 0, -1, 4, -3, 3, 2, 4, -3, 3, 2, 0, 0, 0 };

            for (int i = 1; i <= 105; i++)
            {
                if (i < 33)
                {
                    r.Freq[i, 1] = 10.23e6 * 154.0;
                    r.Wavl[i, 1] = PppConstants.SpeedOfLight / r.Freq[i, 1];
                    r.Freq[i, 2] = 10.23e6 * 120.0;
                    r.Wavl[i, 2] = PppConstants.SpeedOfLight / r.Freq[i, 2];
                }
                else if (i < 60)
                {
                    int k = glok[i - 33];
                    r.Freq[i, 1] = (1602.0 + 0.5625 * k) * 1e6;
                    r.Wavl[i, 1] = PppConstants.SpeedOfLight / r.Freq[i, 1];
                    r.Freq[i, 2] = (1246.0 + 0.4375 * k) * 1e6;
                    r.Wavl[i, 2] = PppConstants.SpeedOfLight / r.Freq[i, 2];
                }
                else if (i < 96)
                {
                    r.Freq[i, 1] = 10.23e6 * 154.0;
                    r.Wavl[i, 1] = PppConstants.SpeedOfLight / r.Freq[i, 1];
                    r.Freq[i, 2] = 10.23e6 * 115.0;
                    r.Wavl[i, 2] = PppConstants.SpeedOfLight / r.Freq[i, 2];
                }
                else
                {
                    r.Freq[i, 1] = 10.23e6 * 152.6;
                    r.Wavl[i, 1] = PppConstants.SpeedOfLight / r.Freq[i, 1];
                    r.Freq[i, 2] = 10.23e6 * 118.0;
                    r.Wavl[i, 2] = PppConstants.SpeedOfLight / r.Freq[i, 2];
                }
            }

            return r;
        }
    }

    public sealed class ObservationHeader
    {
        public string RinexVersion = "";
        public string RinexType = "";
        public string SatelliteSystem = "";
        public double[] ApproxPositionXyz = new double[3];
        public string ReceiverType = "";
        public string AntennaType = "";
        public double[] AntennaDeltaHen = new double[3];
        public int ObservationIntervalSeconds;
        public DateTime FirstObs;
        public DateTime LastObs;
        public string TimeSystem = "";
        public int LeapSeconds;
        public int DayOfYear;
        public ObservationSequence Sequence = new ObservationSequence();
        public int ObservationTypeCount;
        public double Sp3IntervalSeconds;
    }

    public sealed class ObservationSequence
    {
        public int[] Gps = new int[8];
        public int[] Glo = new int[6];
        public int[] Gal = new int[4];
    }

    public sealed class ObservationParseResult
    {
        public ObservationHeader Header = new ObservationHeader();
        public ObservationData Data = new ObservationData();
    }

    public sealed class EpochObservation
    {
        public double EpochSeconds;
        public Dictionary<int, SatelliteObservation> Satellites = new Dictionary<int, SatelliteObservation>();
    }

    public sealed class SatelliteObservation
    {
        public int SatelliteNumber;
        public bool HasP1;
        public bool HasP2;
        public bool HasL1;
        public bool HasL2;
        public double P1;
        public double P2;
        public double L1Meters;
        public double L2Meters;
    }

    public sealed class ObservationData
    {
        public List<EpochObservation> Epochs = new List<EpochObservation>();
    }

    public sealed class Sp3Key
    {
        public int EpochIndex;
        public int SatelliteNumber;

        public override bool Equals(object obj)
        {
            Sp3Key other = obj as Sp3Key;
            if (other == null) return false;
            return EpochIndex == other.EpochIndex && SatelliteNumber == other.SatelliteNumber;
        }

        public override int GetHashCode()
        {
            unchecked
            {
                return EpochIndex * 1000 + SatelliteNumber;
            }
        }
    }

    public sealed class Sp3Record
    {
        public double X;
        public double Y;
        public double Z;
        public double ClockSeconds;
    }

    public sealed class Sp3Data
    {
        public DateTime Date;
        public int EpochCount;
        public double IntervalSeconds;
        public Dictionary<Sp3Key, Sp3Record> Records = new Dictionary<Sp3Key, Sp3Record>();
    }

    public sealed class ClockKey
    {
        public int EpochIndex;
        public int SatelliteNumber;

        public override bool Equals(object obj)
        {
            ClockKey other = obj as ClockKey;
            if (other == null) return false;
            return EpochIndex == other.EpochIndex && SatelliteNumber == other.SatelliteNumber;
        }

        public override int GetHashCode()
        {
            unchecked
            {
                return EpochIndex * 1000 + SatelliteNumber;
            }
        }
    }

    public sealed class ClockData
    {
        public Dictionary<ClockKey, double> Values = new Dictionary<ClockKey, double>();
        public int Rows;
        public int Columns;
        public double IntervalSeconds;
    }

    public sealed class AtxData
    {
        public Dictionary<int, double[]> ReceiverPco = new Dictionary<int, double[]>();
        public string ReceiverType = "";
    }

    public sealed class ImportedData
    {
        public ObservationHeader ObservationHeader = new ObservationHeader();
        public ObservationData Observation = new ObservationData();
        public Sp3Data Sp3Today = new Sp3Data();
        public Sp3Data Sp3Prev = null;
        public Sp3Data Sp3Next = null;
        public ClockData Clock = new ClockData();
        public AtxData Atx = new AtxData();
    }

    public sealed class PppMeasurement
    {
        public int SatelliteNumber;
        public double EpochSeconds;
        public double SatX;
        public double SatY;
        public double SatZ;
        public double SatClockMeters;
        public double PIf;
        public double LIf;
        public double GeometricRange;
        public double ElevationDeg;
        public double AzimuthDeg;
        public double MappingWet;
        public double TropDryMeters;
        public bool Slip;
    }

    public sealed class PreprocessedEpoch
    {
        public double EpochSeconds;
        public List<PppMeasurement> Measurements = new List<PppMeasurement>();
    }

    public sealed class PreprocessResult
    {
        public ObservationHeader Header = new ObservationHeader();
        public List<PreprocessedEpoch> Epochs = new List<PreprocessedEpoch>();
    }

    public sealed class SatelliteState
    {
        public double X;
        public double Y;
        public double Z;
        public double ClockSeconds;
        public double Range;
        public double ElevationDeg;
        public double AzimuthDeg;
    }

    public sealed class FilterSolution
    {
        public double[] Xyz;
        public bool IsConverged;

        public FilterSolution()
        {
            Xyz = new double[3];
        }
    }

    public sealed class PppProcessingService
    {
        private readonly Action<string> _log;

        public PppProcessingService(Action<string> log)
        {
            _log = log;
        }

        public PppResult Run(PppInputFiles files)
        {
            return Run(files, null);
        }

        public PppResult Run(PppInputFiles files, PppEvaluationOptions evaluationOptions)
        {
            _log("1) 导入 RINEX / SP3 / CLK / ATX ...");
            PppOptions options = PppOptions.CreateDefault();
            if (evaluationOptions == null)
                evaluationOptions = new PppEvaluationOptions();

            ImportedData data = new MatlabCompatibleDataImporter(_log).Import(files, options);

            _log("2) 预处理：双频 IF 组合、卫星坐标/钟差、仰角筛选、周跳探测 ...");
            PreprocessResult pre = Preprocessor.Process(data, options, _log);

            _log("3) PPP 滤波：坐标 + 接收机钟差 + 湿延迟 + 每星模糊度 ...");
            List<FilterSolution> solutions = StaticPppKalmanSolver.Solve(pre, options, _log);

            List<double[]> allSolutions = CollectSolutions(solutions, false);
            List<double[]> convergedSolutions = CollectSolutions(solutions, true);

            int startEpoch = evaluationOptions.StatisticsStartEpoch >= 0
                ? evaluationOptions.StatisticsStartEpoch
                : options.BurnInEpochs;

            List<double[]> statisticsSolutions = CollectSolutionsFromIndex(solutions, startEpoch);
            if (statisticsSolutions.Count == 0)
                statisticsSolutions = convergedSolutions.Count > 0 ? convergedSolutions : allSolutions;

            if (statisticsSolutions.Count == 0)
            {
                statisticsSolutions.Add(new double[]
                {
                    data.ObservationHeader.ApproxPositionXyz[0],
                    data.ObservationHeader.ApproxPositionXyz[1],
                    data.ObservationHeader.ApproxPositionXyz[2]
                });
            }

            double[] scatterReference = MeanPosition(statisticsSolutions);
            NeuEvaluationResult scatterEva = NeuEvaluator.Evaluate(statisticsSolutions, scatterReference);

            PppResult result = new PppResult();
            result.UsedEpochCount = solutions.Count;
            result.ConvergedEpochCount = convergedSolutions.Count;
            result.StatisticsEpochCount = statisticsSolutions.Count;
            result.StatisticsStartEpoch = startEpoch;
            result.ScatterReferenceXyz = Copy3(scatterReference);
            result.ScatterNRms = scatterEva.RmsN;
            result.ScatterERms = scatterEva.RmsE;
            result.ScatterURms = scatterEva.RmsU;
            result.ScatterTotalRms = ComputeTotalRms(scatterEva);

            double[] absoluteReference = ResolveAbsoluteReference(evaluationOptions, data);
            if (absoluteReference != null)
            {
                NeuEvaluationResult absoluteEva = NeuEvaluator.Evaluate(statisticsSolutions, absoluteReference);
                result.HasAbsoluteReference = true;
                result.AbsoluteReferenceXyz = Copy3(absoluteReference);
                result.AbsoluteNRms = absoluteEva.RmsN;
                result.AbsoluteERms = absoluteEva.RmsE;
                result.AbsoluteURms = absoluteEva.RmsU;
                result.AbsoluteTotalRms = ComputeTotalRms(absoluteEva);

                result.ReferenceXyz = Copy3(absoluteReference);
                result.ReferenceMode = GetReferenceModeText(evaluationOptions.ReferenceMode);
                result.PrimaryMetricName = "绝对 NEU RMS";
                result.NRms = result.AbsoluteNRms;
                result.ERms = result.AbsoluteERms;
                result.URms = result.AbsoluteURms;
                result.TotalRms = result.AbsoluteTotalRms;
            }
            else
            {
                result.ReferenceXyz = Copy3(scatterReference);
                result.ReferenceMode = GetReferenceModeText(PppReferenceMode.ConvergedMean);
                result.PrimaryMetricName = "内部散布 RMS";
                result.NRms = result.ScatterNRms;
                result.ERms = result.ScatterERms;
                result.URms = result.ScatterURms;
                result.TotalRms = result.ScatterTotalRms;
            }

            result.Summary =
                "当前主显示指标 = " + result.PrimaryMetricName + "；参考坐标模式 = " + result.ReferenceMode + "。" +
                "内部散布 RMS 反映解序列稳定性；仅在提供外部参考坐标时，绝对 NEU RMS 才可解释为相对参考坐标的定位误差。";

            return result;
        }

        private static List<double[]> CollectSolutions(List<FilterSolution> solutions, bool onlyConverged)
        {
            List<double[]> list = new List<double[]>();
            if (solutions == null)
                return list;

            for (int i = 0; i < solutions.Count; i++)
            {
                if (solutions[i] == null)
                    continue;
                if (onlyConverged && !solutions[i].IsConverged)
                    continue;

                list.Add(new double[]
                {
                    solutions[i].Xyz[0],
                    solutions[i].Xyz[1],
                    solutions[i].Xyz[2]
                });
            }

            return list;
        }

        private static List<double[]> CollectSolutionsFromIndex(List<FilterSolution> solutions, int startIndex)
        {
            List<double[]> list = new List<double[]>();
            if (solutions == null)
                return list;

            if (startIndex < 0)
                startIndex = 0;

            for (int i = startIndex; i < solutions.Count; i++)
            {
                if (solutions[i] == null)
                    continue;

                list.Add(new double[]
                {
                    solutions[i].Xyz[0],
                    solutions[i].Xyz[1],
                    solutions[i].Xyz[2]
                });
            }

            return list;
        }

        private static double[] ResolveAbsoluteReference(PppEvaluationOptions evaluationOptions, ImportedData data)
        {
            if (evaluationOptions == null)
                return null;

            if (evaluationOptions.ReferenceMode == PppReferenceMode.RinexApprox)
            {
                return new double[]
                {
                    data.ObservationHeader.ApproxPositionXyz[0],
                    data.ObservationHeader.ApproxPositionXyz[1],
                    data.ObservationHeader.ApproxPositionXyz[2]
                };
            }

            if (evaluationOptions.ReferenceMode == PppReferenceMode.ManualXyz)
            {
                if (evaluationOptions.ManualReferenceXyz != null &&
                    evaluationOptions.ManualReferenceXyz.Length >= 3 &&
                    !(double.IsNaN(evaluationOptions.ManualReferenceXyz[0]) ||
                      double.IsNaN(evaluationOptions.ManualReferenceXyz[1]) ||
                      double.IsNaN(evaluationOptions.ManualReferenceXyz[2])))
                {
                    return new double[]
                    {
                        evaluationOptions.ManualReferenceXyz[0],
                        evaluationOptions.ManualReferenceXyz[1],
                        evaluationOptions.ManualReferenceXyz[2]
                    };
                }
            }

            return null;
        }

        private static string GetReferenceModeText(PppReferenceMode mode)
        {
            switch (mode)
            {
                case PppReferenceMode.RinexApprox:
                    return "RINEX 头近似坐标";
                case PppReferenceMode.ManualXyz:
                    return "手动输入真值 XYZ";
                default:
                    return "收敛后均值";
            }
        }

        private static double ComputeTotalRms(NeuEvaluationResult eva)
        {
            return Math.Sqrt((eva.RmsN * eva.RmsN + eva.RmsE * eva.RmsE + eva.RmsU * eva.RmsU) / 3.0);
        }

        private static double[] Copy3(double[] src)
        {
            double[] dst = new double[3];
            if (src == null || src.Length < 3)
                return dst;

            dst[0] = src[0];
            dst[1] = src[1];
            dst[2] = src[2];
            return dst;
        }

        private static double[] MeanPosition(List<double[]> xs)
        {
            double[] r = new double[3];
            if (xs == null || xs.Count == 0) return r;

            for (int i = 0; i < xs.Count; i++)
            {
                r[0] += xs[i][0];
                r[1] += xs[i][1];
                r[2] += xs[i][2];
            }

            r[0] /= xs.Count;
            r[1] /= xs.Count;
            r[2] /= xs.Count;

            return r;
        }
    }

    public sealed class MatlabCompatibleDataImporter
    {
        private readonly Action<string> _log;

        public MatlabCompatibleDataImporter(Action<string> log)
        {
            _log = log;
        }

        public ImportedData Import(PppInputFiles files, PppOptions options)
        {
            ImportedData result = new ImportedData();

            _log("   读取观测文件...");
            ObservationParseResult obsResult = RinexObservationParser.Parse(files.ObsPath, options);
            result.ObservationHeader = obsResult.Header;
            result.Observation = obsResult.Data;

            _log("   读取当天 SP3...");
            result.Sp3Today = Sp3Parser.Parse(files.Sp3TodayPath, result.ObservationHeader, options);

            if (File.Exists(files.Sp3PrevPath))
            {
                _log("   读取前一天 SP3...");
                result.Sp3Prev = Sp3Parser.Parse(files.Sp3PrevPath, result.ObservationHeader, options);
            }

            if (File.Exists(files.Sp3NextPath))
            {
                _log("   读取后一天 SP3...");
                result.Sp3Next = Sp3Parser.Parse(files.Sp3NextPath, result.ObservationHeader, options);
            }

            _log("   读取 CLK...");
            result.Clock = ClockParser.Parse(files.ClkPath, options);

            _log("   读取 ATX...");
            result.Atx = AtxParser.Parse(files.AtxPath, result.ObservationHeader, options);

            return result;
        }
    }

    public static class Preprocessor
    {
        public static PreprocessResult Process(ImportedData data, PppOptions options, Action<string> log)
        {
            PreprocessResult result = new PreprocessResult();
            result.Header = data.ObservationHeader;

            FrequencyResult fr = SatelliteFrequencies.Get();
            Dictionary<int, double> prevGf = new Dictionary<int, double>();

            int keptEpochs = 0;
            int keptSats = 0;

            for (int i = 0; i < data.Observation.Epochs.Count; i++)
            {
                EpochObservation obsEpoch = data.Observation.Epochs[i];
                PreprocessedEpoch outEpoch = new PreprocessedEpoch();
                outEpoch.EpochSeconds = obsEpoch.EpochSeconds;

                foreach (KeyValuePair<int, SatelliteObservation> kv in obsEpoch.Satellites)
                {
                    SatelliteObservation so = kv.Value;
                    if (!(so.HasP1 && so.HasP2 && so.HasL1 && so.HasL2))
                        continue;

                    SatelliteState satState = SatelliteCalculator.ComputeSatelliteState(
                        data,
                        obsEpoch.EpochSeconds,
                        so.SatelliteNumber,
                        data.ObservationHeader.ApproxPositionXyz,
                        options);

                    if (satState == null)
                        continue;

                    if (satState.ElevationDeg < options.ElevationCutoffDeg)
                        continue;

                    double f1 = fr.Freq[so.SatelliteNumber, 1];
                    double f2 = fr.Freq[so.SatelliteNumber, 2];
                    if (f1 <= 0.0 || f2 <= 0.0)
                        continue;

                    double c1 = (f1 * f1) / (f1 * f1 - f2 * f2);
                    double c2 = (f2 * f2) / (f1 * f1 - f2 * f2);

                    double pIf = c1 * so.P1 - c2 * so.P2;
                    double lIf = c1 * so.L1Meters - c2 * so.L2Meters;
                    double gf = so.L1Meters - so.L2Meters;

                    bool slip = false;
                    double prev;
                    if (prevGf.TryGetValue(so.SatelliteNumber, out prev))
                    {
                        if (Math.Abs(gf - prev) > options.SlipGeometryFreeThresholdMeters)
                            slip = true;
                    }
                    prevGf[so.SatelliteNumber] = gf;

                    TropModelResult trop = TroposphereModel.Compute(
                        data.ObservationHeader.ApproxPositionXyz,
                        satState.ElevationDeg);

                    PppMeasurement m = new PppMeasurement();
                    m.SatelliteNumber = so.SatelliteNumber;
                    m.EpochSeconds = obsEpoch.EpochSeconds;
                    m.SatX = satState.X;
                    m.SatY = satState.Y;
                    m.SatZ = satState.Z;
                    m.SatClockMeters = satState.ClockSeconds * PppConstants.SpeedOfLight;
                    m.PIf = pIf;
                    m.LIf = lIf;
                    m.GeometricRange = satState.Range;
                    m.ElevationDeg = satState.ElevationDeg;
                    m.AzimuthDeg = satState.AzimuthDeg;
                    m.MappingWet = trop.MappingWet;
                    m.TropDryMeters = trop.Zhd * trop.MappingHydro;
                    m.Slip = slip;

                    outEpoch.Measurements.Add(m);
                    keptSats++;
                }

                if (outEpoch.Measurements.Count >= options.MinSatsPerEpoch)
                {
                    result.Epochs.Add(outEpoch);
                    keptEpochs++;
                }
            }

            log("   预处理后有效历元: " + keptEpochs.ToString(CultureInfo.InvariantCulture));
            log("   预处理后有效卫星观测: " + keptSats.ToString(CultureInfo.InvariantCulture));
            return result;
        }
    }

    public static class StaticPppKalmanSolver
    {
        public static List<FilterSolution> Solve(PreprocessResult pre, PppOptions options, Action<string> log)
        {
            List<FilterSolution> solutions = new List<FilterSolution>();
            if (pre == null || pre.Epochs == null || pre.Epochs.Count == 0)
                return solutions;

            int stateCount = 5 + PppConstants.SatelliteCount; // xyz clk zwd ambiguities
            double[] x = new double[stateCount];
            double[,] P = new double[stateCount, stateCount];

            x[0] = pre.Header.ApproxPositionXyz[0];
            x[1] = pre.Header.ApproxPositionXyz[1];
            x[2] = pre.Header.ApproxPositionXyz[2];

            P[0, 0] = 100.0;
            P[1, 1] = 100.0;
            P[2, 2] = 100.0;
            P[3, 3] = options.InitialClockMeters * options.InitialClockMeters;
            P[4, 4] = options.InitialZwdMeters * options.InitialZwdMeters;
            for (int i = 5; i < stateCount; i++)
                P[i, i] = options.InitialAmbMeters * options.InitialAmbMeters;

            int solved = 0;

            for (int epochIndex = 0; epochIndex < pre.Epochs.Count; epochIndex++)
            {
                PreprocessedEpoch ep = pre.Epochs[epochIndex];
                TimeUpdate(P, options);

                for (int j = 0; j < ep.Measurements.Count; j++)
                {
                    PppMeasurement m = ep.Measurements[j];
                    int ambIndex = 5 + (m.SatelliteNumber - 1);
                    if (m.Slip)
                    {
                        P[ambIndex, ambIndex] = options.InitialAmbMeters * options.InitialAmbMeters;
                    }
                }

                for (int outer = 0; outer < options.MaxIterations; outer++)
                {
                    List<double[]> rows = new List<double[]>();
                    List<double> residuals = new List<double>();
                    List<double> variances = new List<double>();

                    for (int j = 0; j < ep.Measurements.Count; j++)
                    {
                        PppMeasurement m = ep.Measurements[j];

                        double[] rec = new double[] { x[0], x[1], x[2] };
                        SatelliteGeometry g = SatelliteGeometry.Compute(rec, m.SatX, m.SatY, m.SatZ);
                        if (g.Range <= 0.0) continue;

                        double codeComputed = g.Range + x[3] + m.TropDryMeters + m.MappingWet * x[4] - m.SatClockMeters;
                        double codeV = m.PIf - codeComputed;

                        double[] hCode = new double[stateCount];
                        hCode[0] = -g.LosX;
                        hCode[1] = -g.LosY;
                        hCode[2] = -g.LosZ;
                        hCode[3] = 1.0;
                        hCode[4] = m.MappingWet;

                        if (Math.Abs(codeV) < options.ResidualOutlierCodeMeters)
                        {
                            rows.Add(hCode);
                            residuals.Add(codeV);
                            variances.Add(MeasurementVariance(options.SigmaCodeMeters, m.ElevationDeg));
                        }

                        int ambIndex = 5 + (m.SatelliteNumber - 1);
                        double phaseComputed = g.Range + x[3] + m.TropDryMeters + m.MappingWet * x[4] - m.SatClockMeters + x[ambIndex];
                        double phaseV = m.LIf - phaseComputed;

                        double[] hPhase = new double[stateCount];
                        hPhase[0] = -g.LosX;
                        hPhase[1] = -g.LosY;
                        hPhase[2] = -g.LosZ;
                        hPhase[3] = 1.0;
                        hPhase[4] = m.MappingWet;
                        hPhase[ambIndex] = 1.0;

                        if (Math.Abs(phaseV) < options.ResidualOutlierPhaseMeters || epochIndex < 3)
                        {
                            rows.Add(hPhase);
                            residuals.Add(phaseV);
                            variances.Add(MeasurementVariance(options.SigmaPhaseMeters, m.ElevationDeg));
                        }
                    }

                    if (rows.Count < 8)
                        break;

                    MeasurementUpdate(x, P, rows, residuals, variances);

                    if (rows.Count > 0)
                    {
                        double dx = Math.Sqrt(
                            residuals.Count > 0 ? 0.0 : 0.0);
                    }

                    if (StateStepNorm(P) < 1e-12)
                        break;
                }

                FilterSolution sol = new FilterSolution();
                sol.Xyz[0] = x[0];
                sol.Xyz[1] = x[1];
                sol.Xyz[2] = x[2];
                sol.IsConverged = epochIndex >= options.BurnInEpochs;
                solutions.Add(sol);
                solved++;
            }

            log("   PPP 输出历元数: " + solved.ToString(CultureInfo.InvariantCulture));
            return solutions;
        }

        private static void TimeUpdate(double[,] P, PppOptions options)
        {
            P[0, 0] += options.ProcessNoisePos2PerEpoch;
            P[1, 1] += options.ProcessNoisePos2PerEpoch;
            P[2, 2] += options.ProcessNoisePos2PerEpoch;
            P[3, 3] += options.ProcessNoiseClock2PerEpoch;
            P[4, 4] += options.ProcessNoiseZwd2PerEpoch;

            for (int i = 5; i < P.GetLength(0); i++)
                P[i, i] += options.ProcessNoiseAmb2PerEpoch;
        }

        private static double MeasurementVariance(double sigma, double elevationDeg)
        {
            double sinEl = Math.Sin(Math.Max(5.0, elevationDeg) * PppConstants.DegToRad);
            return (sigma / sinEl) * (sigma / sinEl);
        }

        private static void MeasurementUpdate(
            double[] x,
            double[,] P,
            List<double[]> rows,
            List<double> v,
            List<double> variances)
        {
            int n = x.Length;
            for (int i = 0; i < rows.Count; i++)
            {
                double[] h = rows[i];
                double R = variances[i];

                double[] Ph = new double[n];
                for (int r = 0; r < n; r++)
                {
                    double s = 0.0;
                    for (int c = 0; c < n; c++)
                        s += P[r, c] * h[c];
                    Ph[r] = s;
                }

                double S = R;
                for (int c = 0; c < n; c++)
                    S += h[c] * Ph[c];
                if (S <= 0.0) continue;

                double[] K = new double[n];
                for (int r = 0; r < n; r++)
                    K[r] = Ph[r] / S;

                double innov = v[i];
                for (int r = 0; r < n; r++)
                    x[r] += K[r] * innov;

                double[,] newP = new double[n, n];
                for (int r = 0; r < n; r++)
                {
                    for (int c = 0; c < n; c++)
                    {
                        newP[r, c] = P[r, c] - K[r] * Ph[c];
                    }
                }

                for (int r = 0; r < n; r++)
                {
                    for (int c = 0; c < n; c++)
                        P[r, c] = newP[r, c];
                }
            }
        }

        private static double StateStepNorm(double[,] P)
        {
            return P[0, 0] + P[1, 1] + P[2, 2];
        }
    }

    public sealed class SatelliteGeometry
    {
        public double Range;
        public double LosX;
        public double LosY;
        public double LosZ;

        public static SatelliteGeometry Compute(double[] rec, double sx, double sy, double sz)
        {
            double dx = sx - rec[0];
            double dy = sy - rec[1];
            double dz = sz - rec[2];
            double rho = Math.Sqrt(dx * dx + dy * dy + dz * dz);

            SatelliteGeometry g = new SatelliteGeometry();
            g.Range = rho;
            if (rho > 0.0)
            {
                g.LosX = dx / rho;
                g.LosY = dy / rho;
                g.LosZ = dz / rho;
            }
            return g;
        }
    }

    public sealed class TropModelResult
    {
        public double Zhd;
        public double MappingHydro;
        public double MappingWet;
    }

    public static class TroposphereModel
    {
        public static TropModelResult Compute(double[] receiverXyz, double elevationDeg)
        {
            double[] llh = CoordinateTransform.XyzToLlh(receiverXyz);
            double lat = llh[0];
            double h = llh[2];

            double p = 1013.25 * Math.Pow(1.0 - 2.2557e-5 * h, 5.2568);
            double zhd = 0.0022768 * p / (1.0 - 0.00266 * Math.Cos(2.0 * lat) - 2.8e-7 * h);

            double sinEl = Math.Sin(Math.Max(3.0, elevationDeg) * PppConstants.DegToRad);
            double map = 1.0 / (sinEl + 0.00143 / (Math.Tan(elevationDeg * PppConstants.DegToRad) + 0.0445));

            TropModelResult r = new TropModelResult();
            r.Zhd = zhd;
            r.MappingHydro = map;
            r.MappingWet = map;
            return r;
        }
    }

    public static class SatelliteCalculator
    {
        public static SatelliteState ComputeSatelliteState(
            ImportedData data,
            double epochSeconds,
            int satNo,
            double[] receiverXyz,
            PppOptions options)
        {
            Sp3Data sp3 = data.Sp3Today;
            if (sp3 == null || sp3.IntervalSeconds <= 0.0)
                return null;

            double tx = epochSeconds;
            double tau = 0.07;

            double x = 0.0;
            double y = 0.0;
            double z = 0.0;
            double clk = 0.0;

            for (int iter = 0; iter < 2; iter++)
            {
                double satTime = tx - tau;
                Sp3Record rec = InterpolateSp3(data, satTime, satNo);
                if (rec == null)
                    return null;

                x = rec.X;
                y = rec.Y;
                z = rec.Z;

                double dx = x - receiverXyz[0];
                double dy = y - receiverXyz[1];
                double dz = z - receiverXyz[2];
                double rho = Math.Sqrt(dx * dx + dy * dy + dz * dz);
                tau = rho / PppConstants.SpeedOfLight;
            }

            ApplyEarthRotation(receiverXyz, ref x, ref y, ref z);

            if (options.PreferClockFile && data.Clock != null)
            {
                double clkSec;
                if (ClockParser.TryInterpolateClock(data.Clock, epochSeconds, satNo, out clkSec))
                    clk = clkSec;
                else
                {
                    Sp3Record rec = InterpolateSp3(data, epochSeconds - tau, satNo);
                    if (rec == null) return null;
                    clk = rec.ClockSeconds;
                }
            }
            else
            {
                Sp3Record rec = InterpolateSp3(data, epochSeconds - tau, satNo);
                if (rec == null) return null;
                clk = rec.ClockSeconds;
            }

            double[] enu = CoordinateTransform.XyzDiffToEnu(receiverXyz, new double[] { x, y, z });
            double e = enu[0];
            double n = enu[1];
            double u = enu[2];
            double horiz = Math.Sqrt(e * e + n * n);
            double el = Math.Atan2(u, horiz) * PppConstants.RadToDeg;
            double az = Math.Atan2(e, n) * PppConstants.RadToDeg;
            if (az < 0.0) az += 360.0;

            SatelliteState s = new SatelliteState();
            s.X = x;
            s.Y = y;
            s.Z = z;
            s.ClockSeconds = clk;
            s.Range = Math.Sqrt((x - receiverXyz[0]) * (x - receiverXyz[0]) +
                                (y - receiverXyz[1]) * (y - receiverXyz[1]) +
                                (z - receiverXyz[2]) * (z - receiverXyz[2]));
            s.ElevationDeg = el;
            s.AzimuthDeg = az;
            return s;
        }

        private static void ApplyEarthRotation(double[] rec, ref double x, ref double y, ref double z)
        {
            double rho = Math.Sqrt((x - rec[0]) * (x - rec[0]) + (y - rec[1]) * (y - rec[1]) + (z - rec[2]) * (z - rec[2]));
            double tau = rho / PppConstants.SpeedOfLight;
            double ang = PppConstants.OmegaEarth * tau;
            double cosA = Math.Cos(ang);
            double sinA = Math.Sin(ang);

            double xr = cosA * x + sinA * y;
            double yr = -sinA * x + cosA * y;
            x = xr;
            y = yr;
        }

        private static Sp3Record InterpolateSp3(ImportedData data, double sec, int satNo)
        {
            List<Tuple<double, Sp3Record>> pts = GatherSp3Points(data, sec, satNo);
            if (pts.Count < 2) return null;

            pts.Sort((a, b) => a.Item1.CompareTo(b.Item1));
            if (pts.Count > 8)
            {
                pts = pts.OrderBy(p => Math.Abs(p.Item1 - sec)).Take(8).OrderBy(p => p.Item1).ToList();
            }

            Sp3Record r = new Sp3Record();
            r.X = Lagrange(sec, pts, p => p.Item2.X);
            r.Y = Lagrange(sec, pts, p => p.Item2.Y);
            r.Z = Lagrange(sec, pts, p => p.Item2.Z);
            r.ClockSeconds = Lagrange(sec, pts, p => p.Item2.ClockSeconds);
            return r;
        }

        private static List<Tuple<double, Sp3Record>> GatherSp3Points(ImportedData data, double sec, int satNo)
        {
            List<Tuple<double, Sp3Record>> pts = new List<Tuple<double, Sp3Record>>();
            AppendSp3Points(pts, data.Sp3Prev, sec - 86400.0, satNo);
            AppendSp3Points(pts, data.Sp3Today, sec, satNo);
            AppendSp3Points(pts, data.Sp3Next, sec + 86400.0, satNo);
            return pts;
        }

        private static void AppendSp3Points(List<Tuple<double, Sp3Record>> pts, Sp3Data sp3, double sec, int satNo)
        {
            if (sp3 == null || sp3.IntervalSeconds <= 0.0) return;
            int center = (int)Math.Round(sec / sp3.IntervalSeconds) + 1;

            for (int k = center - 4; k <= center + 4; k++)
            {
                if (k < 1) continue;

                Sp3Key key = new Sp3Key();
                key.EpochIndex = k;
                key.SatelliteNumber = satNo;

                Sp3Record rec;
                if (sp3.Records.TryGetValue(key, out rec))
                {
                    double t = (k - 1) * sp3.IntervalSeconds;
                    pts.Add(Tuple.Create(t, rec));
                }
            }
        }

        private static double Lagrange(double t, List<Tuple<double, Sp3Record>> pts, Func<Tuple<double, Sp3Record>, double> selector)
        {
            double y = 0.0;
            for (int i = 0; i < pts.Count; i++)
            {
                double li = 1.0;
                double ti = pts[i].Item1;
                for (int j = 0; j < pts.Count; j++)
                {
                    if (i == j) continue;
                    double tj = pts[j].Item1;
                    if (Math.Abs(ti - tj) < 1e-12) continue;
                    li *= (t - tj) / (ti - tj);
                }
                y += li * selector(pts[i]);
            }
            return y;
        }
    }

    public static class RinexObservationParser
    {
        public static ObservationParseResult Parse(string obsPath, PppOptions options)
        {
            ObservationParseResult result = new ObservationParseResult();
            using (StreamReader sr = new StreamReader(obsPath))
            {
                string line;
                while ((line = sr.ReadLine()) != null)
                {
                    string label = line.Length >= 61 ? line.Substring(60).Trim() : "";

                    if (label == "RINEX VERSION / TYPE")
                    {
                        result.Header.RinexVersion = SafeSubstring(line, 0, 10).Trim();
                        result.Header.RinexType = SafeSubstring(line, 20, 1).Trim();
                        result.Header.SatelliteSystem = SafeSubstring(line, 40, 1).Trim();
                    }
                    else if (label == "APPROX POSITION XYZ")
                    {
                        result.Header.ApproxPositionXyz = ParseThreeDoubles(SafeSubstring(line, 0, 60));
                    }
                    else if (label == "REC # / TYPE / VERS")
                    {
                        result.Header.ReceiverType = SafeSubstring(line, 20, 20).Trim();
                    }
                    else if (label == "ANT # / TYPE")
                    {
                        result.Header.AntennaType = SafeSubstring(line, 20, 20).Trim();
                    }
                    else if (label == "ANTENNA: DELTA H/E/N")
                    {
                        result.Header.AntennaDeltaHen = ParseThreeDoubles(SafeSubstring(line, 0, 60));
                    }
                    else if (label == "# / TYPES OF OBSERV")
                    {
                        ParseRinex2ObservationTypes(sr, line, result.Header);
                    }
                    else if (label == "INTERVAL")
                    {
                        result.Header.ObservationIntervalSeconds = (int)Math.Round(ParseDouble(SafeSubstring(line, 0, 10)));
                    }
                    else if (label == "TIME OF FIRST OBS")
                    {
                        result.Header.FirstObs = ParseTimeOfObsLine(line);
                        result.Header.TimeSystem = SafeSubstring(line, 43, 17).Trim();
                    }
                    else if (label == "TIME OF LAST OBS")
                    {
                        result.Header.LastObs = ParseTimeOfObsLine(line);
                    }
                    else if (label == "LEAP SECONDS")
                    {
                        int leap;
                        int.TryParse(SafeSubstring(line, 0, 6).Trim(), out leap);
                        result.Header.LeapSeconds = leap;
                    }
                    else if (label == "END OF HEADER")
                    {
                        break;
                    }
                }

                result.Header.DayOfYear = result.Header.FirstObs.DayOfYear;
                FrequencyResult fr = SatelliteFrequencies.Get();

                while ((line = sr.ReadLine()) != null)
                {
                    if (string.IsNullOrWhiteSpace(line)) continue;
                    if (line.StartsWith(">"))
                    {
                        ParseRinex3Body(sr, line, result.Data, result.Header, fr.Wavl, options);
                    }
                    else
                    {
                        ParseRinex2Body(sr, line, result.Data, result.Header, fr.Wavl, options);
                    }
                }
            }

            return result;
        }

        private static void ParseRinex2ObservationTypes(StreamReader sr, string firstLine, ObservationHeader header)
        {
            int count = int.Parse(SafeSubstring(firstLine, 0, 6).Trim());
            header.ObservationTypeCount = count;

            int read = 0;
            string current = firstLine;
            int pos = 10;

            while (read < count)
            {
                while (pos + 2 <= current.Length && read < count)
                {
                    string obsType = SafeSubstring(current, pos, 2).Trim();
                    if (!string.IsNullOrWhiteSpace(obsType))
                    {
                        read++;
                        MapObservationType(obsType, read, header.Sequence);
                    }

                    pos += 6;
                    if (pos > 58) break;
                }

                if (read < count)
                {
                    current = sr.ReadLine();
                    if (current == null) break;
                    pos = 10;
                }
            }
        }

        private static void ParseRinex2Body(StreamReader sr, string epochLine, ObservationData data, ObservationHeader header, double[,] wavl, PppOptions options)
        {
            if (string.IsNullOrWhiteSpace(epochLine) || epochLine.Length < 32)
                return;

            double[] epochNumbers = SplitDoubles(SafeSubstring(epochLine, 0, 32));
            if (epochNumbers.Length < 8)
                return;

            int year2 = (int)epochNumbers[0];
            int year = year2 < 80 ? 2000 + year2 : 1900 + year2;
            int month = (int)epochNumbers[1];
            int day = (int)epochNumbers[2];
            int hour = (int)epochNumbers[3];
            int minute = (int)epochNumbers[4];
            double second = epochNumbers[5];
            int flag = (int)epochNumbers[6];
            int satCount = (int)epochNumbers[7];

            if (flag != 0 && flag != 1)
                return;

            EpochObservation epoch = new EpochObservation();
            epoch.EpochSeconds = hour * 3600.0 + minute * 60.0 + second;

            List<int> satNos = new List<int>();
            string current = epochLine;
            int j = 32;

            while (satNos.Count < satCount)
            {
                if (j + 3 > current.Length)
                {
                    current = sr.ReadLine();
                    if (current == null) break;
                    j = 32;
                    continue;
                }

                string satToken = SafeSubstring(current, j, 3).Trim();
                if (!string.IsNullOrWhiteSpace(satToken))
                {
                    int satNo = MapRinexSatTokenToInternal(satToken, options);
                    if (satNo > 0)
                        satNos.Add(satNo);
                }
                j += 3;
            }

            foreach (int satNo in satNos)
            {
                int linesNeeded = (int)Math.Ceiling(header.ObservationTypeCount / 5.0);
                List<double> values = new List<double>();

                for (int k = 0; k < linesNeeded; k++)
                {
                    string obsLine = sr.ReadLine();
                    if (obsLine == null) break;

                    for (int n = 0; n < 5; n++)
                    {
                        int st = 16 * n;
                        if (st >= obsLine.Length) break;

                        string field = SafeSubstring(obsLine, st, 14).Trim();
                        values.Add(string.IsNullOrWhiteSpace(field) ? 0.0 : ParseDouble(field));
                    }
                }

                SatelliteObservation satObs = BuildSatelliteObservation(satNo, values, header.Sequence, wavl);
                epoch.Satellites[satNo] = satObs;
            }

            data.Epochs.Add(epoch);
        }

        private static void ParseRinex3Body(StreamReader sr, string epochLine, ObservationData data, ObservationHeader header, double[,] wavl, PppOptions options)
        {
            string[] parts = epochLine.Split(new char[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
            if (parts.Length < 9) return;

            int satCount = int.Parse(parts[8]);
            EpochObservation epoch = new EpochObservation();
            epoch.EpochSeconds = double.Parse(parts[4], CultureInfo.InvariantCulture) * 3600.0
                               + double.Parse(parts[5], CultureInfo.InvariantCulture) * 60.0
                               + double.Parse(parts[6], CultureInfo.InvariantCulture);

            for (int i = 0; i < satCount; i++)
            {
                string obsLine = sr.ReadLine();
                if (string.IsNullOrWhiteSpace(obsLine) || obsLine.Length < 3) continue;

                int satNo = MapRinexSatTokenToInternal(obsLine.Substring(0, 3), options);
                if (satNo <= 0) continue;

                string sys = obsLine.Substring(0, 1);
                string body = obsLine.Length > 3 ? obsLine.Substring(3) : "";
                List<double> values = ParseRinex3ObsValues(body);
                SatelliteObservation satObs = BuildSatelliteObservationRinex3(satNo, sys, values, wavl);
                epoch.Satellites[satNo] = satObs;
            }

            data.Epochs.Add(epoch);
        }

        private static List<double> ParseRinex3ObsValues(string body)
        {
            List<double> values = new List<double>();
            for (int i = 0; i < body.Length; i += 16)
            {
                string field = SafeSubstring(body, i, 14).Trim();
                values.Add(string.IsNullOrWhiteSpace(field) ? 0.0 : ParseDouble(field));
            }
            return values;
        }

        private static SatelliteObservation BuildSatelliteObservationRinex3(int satNo, string sys, List<double> values, double[,] wavl)
        {
            SatelliteObservation sat = new SatelliteObservation();
            sat.SatelliteNumber = satNo;

            if (values.Count >= 4)
            {
                sat.P1 = values[0];
                sat.P2 = values[1];
                sat.HasP1 = sat.P1 != 0.0;
                sat.HasP2 = sat.P2 != 0.0;

                double l1cyc = values.Count > 2 ? values[2] : 0.0;
                double l2cyc = values.Count > 3 ? values[3] : 0.0;

                sat.HasL1 = l1cyc != 0.0;
                sat.HasL2 = l2cyc != 0.0;
                sat.L1Meters = l1cyc * wavl[satNo, 1];
                sat.L2Meters = l2cyc * wavl[satNo, 2];
            }
            return sat;
        }

        private static SatelliteObservation BuildSatelliteObservation(int satNo, List<double> values, ObservationSequence seq, double[,] wavl)
        {
            SatelliteObservation sat = new SatelliteObservation();
            sat.SatelliteNumber = satNo;

            if (satNo < 33)
            {
                SetValue(values, seq.Gps[3], ref sat.HasP1, ref sat.P1);
                SetValue(values, seq.Gps[4], ref sat.HasP2, ref sat.P2);

                double l1 = 0.0; bool hl1 = false;
                SetValue(values, seq.Gps[5], ref hl1, ref l1);
                sat.HasL1 = hl1;
                sat.L1Meters = l1 * wavl[satNo, 1];

                double l2 = 0.0; bool hl2 = false;
                SetValue(values, seq.Gps[6], ref hl2, ref l2);
                sat.HasL2 = hl2;
                sat.L2Meters = l2 * wavl[satNo, 2];
            }
            else if (satNo < 60)
            {
                SetValue(values, seq.Glo[2], ref sat.HasP1, ref sat.P1);
                SetValue(values, seq.Glo[3], ref sat.HasP2, ref sat.P2);

                double l1 = 0.0; bool hl1 = false;
                SetValue(values, seq.Glo[4], ref hl1, ref l1);
                sat.HasL1 = hl1;
                sat.L1Meters = l1 * wavl[satNo, 1];

                double l2 = 0.0; bool hl2 = false;
                SetValue(values, seq.Glo[5], ref hl2, ref l2);
                sat.HasL2 = hl2;
                sat.L2Meters = l2 * wavl[satNo, 2];
            }
            else if (satNo < 96)
            {
                SetValue(values, seq.Gal[0], ref sat.HasP1, ref sat.P1);
                SetValue(values, seq.Gal[1], ref sat.HasP2, ref sat.P2);

                double l1 = 0.0; bool hl1 = false;
                SetValue(values, seq.Gal[2], ref hl1, ref l1);
                sat.HasL1 = hl1;
                sat.L1Meters = l1 * wavl[satNo, 1];

                double l2 = 0.0; bool hl2 = false;
                SetValue(values, seq.Gal[3], ref hl2, ref l2);
                sat.HasL2 = hl2;
                sat.L2Meters = l2 * wavl[satNo, 2];
            }

            return sat;
        }

        private static void SetValue(List<double> arr, int idx, ref bool hasValue, ref double value)
        {
            if (idx > 0 && idx <= arr.Count && arr[idx - 1] != 0.0)
            {
                hasValue = true;
                value = arr[idx - 1];
            }
        }

        private static void MapObservationType(string obsType, int index, ObservationSequence seq)
        {
            if (obsType == "C1") { seq.Gps[0] = index; seq.Glo[0] = index; seq.Gal[0] = index; }
            else if (obsType == "C2") { seq.Gps[1] = index; seq.Glo[1] = index; }
            else if (obsType == "C5") { seq.Gps[2] = index; seq.Gal[1] = index; }
            else if (obsType == "P1") { seq.Gps[3] = index; seq.Glo[2] = index; }
            else if (obsType == "P2") { seq.Gps[4] = index; seq.Glo[3] = index; }
            else if (obsType == "L1") { seq.Gps[5] = index; seq.Glo[4] = index; seq.Gal[2] = index; }
            else if (obsType == "L2") { seq.Gps[6] = index; seq.Glo[5] = index; }
            else if (obsType == "L5") { seq.Gps[7] = index; seq.Gal[3] = index; }
        }

        private static int MapRinexSatTokenToInternal(string token, PppOptions options)
        {
            token = token.Trim();
            if (string.IsNullOrWhiteSpace(token)) return -1;

            char sys = token[0];
            if (char.IsDigit(sys))
            {
                int legacy;
                if (int.TryParse(token, out legacy)) return legacy;
                return -1;
            }

            int prn = int.Parse(token.Substring(1));
            if (sys == 'G' && options.UseGps && prn <= 32) return prn;
            if (sys == 'R' && options.UseGlonass && prn <= 27) return 32 + prn;
            if (sys == 'E' && options.UseGalileo && prn <= 36) return 32 + 27 + prn;
            if (sys == 'C' && options.UseBds) return 95 + prn;

            return -1;
        }

        private static DateTime ParseTimeOfObsLine(string line)
        {
            double[] nums = SplitDoubles(SafeSubstring(line, 0, 43));
            return new DateTime((int)nums[0], (int)nums[1], (int)nums[2], (int)nums[3], (int)nums[4], 0).AddSeconds(nums[5]);
        }

        private static string SafeSubstring(string s, int start, int length)
        {
            if (start >= s.Length) return "";
            if (start + length > s.Length) length = s.Length - start;
            return s.Substring(start, length);
        }

        private static double[] SplitDoubles(string input)
        {
            List<double> list = new List<double>();
            string[] parts = input.Split(new char[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);

            foreach (string p in parts)
            {
                double v;
                if (double.TryParse(p.Replace('D', 'E'), NumberStyles.Any, CultureInfo.InvariantCulture, out v))
                    list.Add(v);
            }

            return list.ToArray();
        }

        private static double ParseDouble(string s)
        {
            double v;
            return double.TryParse(s.Replace('D', 'E'), NumberStyles.Any, CultureInfo.InvariantCulture, out v) ? v : 0.0;
        }

        private static double[] ParseThreeDoubles(string s)
        {
            double[] arr = SplitDoubles(s);
            double[] r = new double[3];
            if (arr.Length > 0) r[0] = arr[0];
            if (arr.Length > 1) r[1] = arr[1];
            if (arr.Length > 2) r[2] = arr[2];
            return r;
        }
    }

    public static class Sp3Parser
    {
        public static Sp3Data Parse(string path, ObservationHeader header, PppOptions options)
        {
            Sp3Data data = new Sp3Data();
            using (StreamReader sr = new StreamReader(path))
            {
                string line;
                int satCountInHeader = 0;

                while ((line = sr.ReadLine()) != null)
                {
                    if (line.StartsWith("#") && !line.StartsWith("##"))
                    {
                        string[] dateNums = SafeSlice(line, 3, 28).Split(new char[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                        if (dateNums.Length >= 6)
                        {
                            data.Date = new DateTime(
                                int.Parse(dateNums[0]),
                                int.Parse(dateNums[1]),
                                int.Parse(dateNums[2]),
                                int.Parse(dateNums[3]),
                                int.Parse(dateNums[4]),
                                0).AddSeconds(double.Parse(dateNums[5], CultureInfo.InvariantCulture));
                        }

                        int epochn;
                        int.TryParse(SafeSlice(line, 32, 7).Trim(), out epochn);
                        data.EpochCount = epochn;
                    }
                    else if (line.StartsWith("##"))
                    {
                        data.IntervalSeconds = ParseDouble(SafeSlice(line, 24, 14));
                        header.Sp3IntervalSeconds = data.IntervalSeconds;
                    }
                    else if (line.StartsWith("+"))
                    {
                        int satn;
                        if (int.TryParse(SafeSlice(line, 4, 2).Trim(), out satn))
                            satCountInHeader = satn;
                    }
                    else if (line.StartsWith("*"))
                    {
                        string[] ep = line.Substring(2).Split(new char[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                        if (ep.Length < 6) continue;

                        int hour = int.Parse(ep[3]);
                        int minute = int.Parse(ep[4]);
                        double second = double.Parse(ep[5], CultureInfo.InvariantCulture);
                        int epIndex = (int)Math.Round((hour * 3600 + minute * 60 + second) / data.IntervalSeconds) + 1;

                        for (int i = 0; i < satCountInHeader; i++)
                        {
                            string satLine = sr.ReadLine();
                            if (string.IsNullOrWhiteSpace(satLine) || satLine.Length < 4 || satLine[0] != 'P')
                                continue;

                            int satNo = MapSp3Satellite(satLine, options);
                            if (satNo <= 0) continue;

                            string[] vals = satLine.Substring(4).Split(new char[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                            if (vals.Length < 4) continue;

                            Sp3Key key = new Sp3Key();
                            key.EpochIndex = epIndex;
                            key.SatelliteNumber = satNo;

                            Sp3Record rec = new Sp3Record();
                            rec.X = double.Parse(vals[0], CultureInfo.InvariantCulture) * 1000.0;
                            rec.Y = double.Parse(vals[1], CultureInfo.InvariantCulture) * 1000.0;
                            rec.Z = double.Parse(vals[2], CultureInfo.InvariantCulture) * 1000.0;
                            rec.ClockSeconds = vals[3] == "999999.999999" ? 0.0 : double.Parse(vals[3], CultureInfo.InvariantCulture) * 1e-6;

                            data.Records[key] = rec;
                        }
                    }
                }
            }

            return data;
        }

        private static int MapSp3Satellite(string line, PppOptions options)
        {
            char sys = line[1];
            int prn = int.Parse(line.Substring(2, 2));

            if (sys == 'G' && options.UseGps && prn <= 32) return prn;
            if (sys == 'R' && options.UseGlonass && prn <= 27) return 32 + prn;
            if (sys == 'E' && options.UseGalileo && prn <= 36) return 32 + 27 + prn;

            return -1;
        }

        private static string SafeSlice(string s, int start, int length)
        {
            if (start >= s.Length) return "";
            if (start + length > s.Length) length = s.Length - start;
            return s.Substring(start, length);
        }

        private static double ParseDouble(string s)
        {
            double v;
            return double.TryParse(s.Replace('D', 'E'), NumberStyles.Any, CultureInfo.InvariantCulture, out v) ? v : 0.0;
        }
    }

    public static class ClockParser
    {
        public static ClockData Parse(string path, PppOptions options)
        {
            ClockData data = new ClockData();
            data.Rows = 86400 / options.ClockIntervalSeconds;
            data.Columns = PppConstants.SatelliteCount;
            data.IntervalSeconds = options.ClockIntervalSeconds;

            using (StreamReader sr = new StreamReader(path))
            {
                string line;
                while ((line = sr.ReadLine()) != null)
                {
                    if (!line.StartsWith("AS ")) continue;

                    char sys = line.Length > 3 ? line[3] : '\0';
                    int satNo = MapSatellite(line, sys, options);
                    if (satNo <= 0) continue;

                    string[] vals = line.Substring(5).Split(new char[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                    if (vals.Length < 9) continue;

                    double seconds = double.Parse(vals[4], CultureInfo.InvariantCulture) * 3600.0
                                   + double.Parse(vals[5], CultureInfo.InvariantCulture) * 60.0
                                   + double.Parse(vals[6], CultureInfo.InvariantCulture);

                    int epIndex = (int)Math.Round(seconds / options.ClockIntervalSeconds) + 1;
                    double clk = double.Parse(vals[8], CultureInfo.InvariantCulture);

                    ClockKey key = new ClockKey();
                    key.EpochIndex = epIndex;
                    key.SatelliteNumber = satNo;

                    data.Values[key] = clk;
                }
            }

            return data;
        }

        public static bool TryInterpolateClock(ClockData data, double epochSeconds, int satNo, out double clkSec)
        {
            clkSec = 0.0;
            if (data == null || data.IntervalSeconds <= 0.0) return false;

            int idx0 = (int)Math.Floor(epochSeconds / data.IntervalSeconds) + 1;
            int idx1 = idx0 + 1;

            ClockKey k0 = new ClockKey { EpochIndex = idx0, SatelliteNumber = satNo };
            ClockKey k1 = new ClockKey { EpochIndex = idx1, SatelliteNumber = satNo };

            double c0, c1;
            bool ok0 = data.Values.TryGetValue(k0, out c0);
            bool ok1 = data.Values.TryGetValue(k1, out c1);

            if (ok0 && ok1)
            {
                double t0 = (idx0 - 1) * data.IntervalSeconds;
                double t1 = (idx1 - 1) * data.IntervalSeconds;
                double a = Math.Abs(t1 - t0) < 1e-12 ? 0.0 : (epochSeconds - t0) / (t1 - t0);
                clkSec = c0 + a * (c1 - c0);
                return true;
            }

            if (ok0)
            {
                clkSec = c0;
                return true;
            }

            if (ok1)
            {
                clkSec = c1;
                return true;
            }

            return false;
        }

        private static int MapSatellite(string line, char sys, PppOptions options)
        {
            int prn;
            if (!int.TryParse(line.Substring(4, 2).Trim(), out prn))
                return -1;

            if (sys == 'G' && options.UseGps && prn <= 32) return prn;
            if (sys == 'R' && options.UseGlonass && prn <= 27) return 32 + prn;
            if (sys == 'E' && options.UseGalileo && prn <= 36) return 32 + 27 + prn;

            return -1;
        }
    }

    public static class AtxParser
    {
        public static AtxData Parse(string path, ObservationHeader header, PppOptions options)
        {
            AtxData data = new AtxData();
            data.ReceiverType = header.ReceiverType;

            using (StreamReader sr = new StreamReader(path))
            {
                string line;
                bool inReceiver = false;
                bool matchedReceiver = false;

                while ((line = sr.ReadLine()) != null)
                {
                    string label = line.Length >= 61 ? line.Substring(60).Trim() : "";
                    if (label == "START OF ANTENNA")
                    {
                        inReceiver = false;
                        matchedReceiver = false;
                    }
                    else if (label == "TYPE / SERIAL NO")
                    {
                        string antType = SafeSubstring(line, 0, 20).Trim();
                        if (!string.IsNullOrWhiteSpace(header.AntennaType) && antType.StartsWith(header.AntennaType.Trim(), StringComparison.OrdinalIgnoreCase))
                        {
                            inReceiver = true;
                            matchedReceiver = true;
                        }
                    }
                    else if (matchedReceiver && label == "NORTH / EAST / UP")
                    {
                        double[] neu = ParseThreeDoubles(SafeSubstring(line, 0, 30));
                        // ATX stores mm in many files; convert conservatively if magnitude large.
                        if (Math.Abs(neu[0]) > 10.0 || Math.Abs(neu[1]) > 10.0 || Math.Abs(neu[2]) > 10.0)
                        {
                            neu[0] /= 1000.0;
                            neu[1] /= 1000.0;
                            neu[2] /= 1000.0;
                        }

                        data.ReceiverPco[1] = new double[] { neu[1], neu[0], neu[2] };
                        data.ReceiverPco[2] = new double[] { neu[1], neu[0], neu[2] };
                    }
                    else if (label == "END OF ANTENNA")
                    {
                        if (matchedReceiver)
                            break;
                        inReceiver = false;
                    }
                }
            }

            return data;
        }

        private static string SafeSubstring(string s, int start, int length)
        {
            if (start >= s.Length) return "";
            if (start + length > s.Length) length = s.Length - start;
            return s.Substring(start, length);
        }

        private static double[] ParseThreeDoubles(string s)
        {
            string[] parts = s.Split(new char[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
            double[] r = new double[3];
            for (int i = 0; i < Math.Min(3, parts.Length); i++)
            {
                double.TryParse(parts[i].Replace('D', 'E'), NumberStyles.Any, CultureInfo.InvariantCulture, out r[i]);
            }
            return r;
        }
    }

    public sealed class NeuEvaluationResult
    {
        public double RmsN;
        public double RmsE;
        public double RmsU;
    }

    public static class NeuEvaluator
    {
        public static NeuEvaluationResult Evaluate(List<double[]> xyzs, double[] referenceXyz)
        {
            NeuEvaluationResult r = new NeuEvaluationResult();
            if (xyzs == null || xyzs.Count == 0) return r;

            double sN = 0.0;
            double sE = 0.0;
            double sU = 0.0;

            for (int i = 0; i < xyzs.Count; i++)
            {
                double[] enu = CoordinateTransform.XyzDiffToEnu(referenceXyz, xyzs[i]);
                sE += enu[0] * enu[0];
                sN += enu[1] * enu[1];
                sU += enu[2] * enu[2];
            }

            r.RmsN = Math.Sqrt(sN / xyzs.Count);
            r.RmsE = Math.Sqrt(sE / xyzs.Count);
            r.RmsU = Math.Sqrt(sU / xyzs.Count);
            return r;
        }
    }

    public static class CoordinateTransform
    {
        private const double A = 6378137.0;
        private const double F = 1.0 / 298.257223563;
        private const double E2 = F * (2.0 - F);

        public static double[] XyzToLlh(double[] xyz)
        {
            double x = xyz[0];
            double y = xyz[1];
            double z = xyz[2];

            double lon = Math.Atan2(y, x);
            double p = Math.Sqrt(x * x + y * y);
            double lat = Math.Atan2(z, p * (1.0 - E2));

            for (int i = 0; i < 8; i++)
            {
                double sinLat = Math.Sin(lat);
                double N = A / Math.Sqrt(1.0 - E2 * sinLat * sinLat);
                lat = Math.Atan2(z + E2 * N * sinLat, p);
            }

            double sin = Math.Sin(lat);
            double Nf = A / Math.Sqrt(1.0 - E2 * sin * sin);
            double h = p / Math.Cos(lat) - Nf;

            return new double[] { lat, lon, h };
        }

        public static double[] XyzDiffToEnu(double[] refXyz, double[] xyz)
        {
            double[] llh = XyzToLlh(refXyz);
            double lat = llh[0];
            double lon = llh[1];

            double dx = xyz[0] - refXyz[0];
            double dy = xyz[1] - refXyz[1];
            double dz = xyz[2] - refXyz[2];

            double sinLat = Math.Sin(lat);
            double cosLat = Math.Cos(lat);
            double sinLon = Math.Sin(lon);
            double cosLon = Math.Cos(lon);

            double e = -sinLon * dx + cosLon * dy;
            double n = -sinLat * cosLon * dx - sinLat * sinLon * dy + cosLat * dz;
            double u = cosLat * cosLon * dx + cosLat * sinLon * dy + sinLat * dz;

            return new double[] { e, n, u };
        }
    }
}
