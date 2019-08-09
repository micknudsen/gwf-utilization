[![Build Status](https://travis-ci.org/micknudsen/gwf-utilization.svg?branch=master)](https://travis-ci.org/micknudsen/gwf-utilization) [![Coverage Status](https://coveralls.io/repos/github/micknudsen/gwf-utilization/badge.svg?branch=master)](https://coveralls.io/github/micknudsen/gwf-utilization?branch=master)

# gwf-utilization

Trying to write a [gwf](http://gwf.readthedocs.io/en/latest/) plugin for providing information about how well allocated resources have been used. Ideas and comments are more than welcome!

```
+----------------------------------------+-------+----------------+---------------+--------------+-------------+----------------+---------------+------------+----------+-------+
| Target                                 | Cores | Walltime Alloc | Walltime Used | Memory Alloc | Memory Used | CPU Time Alloc | CPU Time Used | Walltime % | Memory % | CPU % |
+========================================+=======+================+===============+==============+=============+================+===============+============+==========+=======+
| TrimAdapterSequences_SampleName_Lane_1 |     4 |       00:15:00 |      00:03:59 |       1.0 GB |   230.27 MB |       01:00:00 |      00:15:56 |       26.6 |     22.5 |  26.6 |
| TrimAdapterSequences_SampleName_Lane_2 |     4 |       00:15:00 |      00:03:54 |       1.0 GB |   224.59 MB |       01:00:00 |      00:15:36 |       26.0 |     21.9 |  26.0 |
| TrimAdapterSequences_SampleName_Lane_3 |     4 |       00:15:00 |      00:03:38 |       1.0 GB |   211.38 MB |       01:00:00 |      00:14:32 |       24.2 |     20.6 |  24.2 |
| TrimAdapterSequences_SampleName_Lane_4 |     4 |       00:15:00 |      00:03:40 |       1.0 GB |   212.73 MB |       01:00:00 |      00:14:40 |       24.4 |     20.8 |  24.4 |
| MergeTrimmedFastqFiles_SampleName      |     1 |       00:05:00 |      00:00:30 |     128.0 MB |    936.0 KB |       00:05:00 |      00:00:30 |       10.0 |      0.7 |  10.0 |
| StarAlignment_SampleName               |    36 |       00:30:00 |      00:08:44 |      64.0 GB |    44.12 GB |       18:00:00 |      05:14:24 |       29.1 |     68.9 |  29.1 |
| StarFusion_SampleName                  |    16 |       01:00:00 |      00:29:25 |      64.0 GB |    41.19 GB |       16:00:00 |      07:50:40 |       49.0 |     64.4 |  49.0 |
+----------------------------------------+-------+----------------+---------------+--------------+-------------+----------------+---------------+------------+----------+-------+
```
