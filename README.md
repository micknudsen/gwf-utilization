[![install with conda](https://img.shields.io/badge/install%20with-conda-brightgreen.svg?style=flat)](https://conda.anaconda.org/micknudsen) ![CI](https://github.com/micknudsen/gwf-utilization/workflows/CI/badge.svg?branch=master) [![Coverage Status](https://coveralls.io/repos/github/micknudsen/gwf-utilization/badge.svg?branch=master)](https://coveralls.io/github/micknudsen/gwf-utilization?branch=master)

# gwf-utilization

This is a [gwf](http://gwf.readthedocs.io/en/latest/) plugin for providing information about how well allocated resources have been used. Note that only the _Slurm_ backend is supported.


```
$ gwf utilization
+---------------------------------------+-------+----------------+---------------+--------------+-------------+----------------+---------------+------------+----------+-------+
| Target                                | Cores | Walltime Alloc | Walltime Used | Memory Alloc | Memory Used | CPU Time Alloc | CPU Time Used | Walltime % | Memory % | CPU % |
+=======================================+=======+================+===============+==============+=============+================+===============+============+==========+=======+
| TrimAdapterSequences_SampleName_Lane1 |    16 |       00:15:00 |      00:02:58 |       1.0 GB |   819.68 MB |       04:00:00 |      00:15:08 |       19.8 |     80.0 |   6.3 |
| TrimAdapterSequences_SampleName_Lane2 |    16 |       00:15:00 |      00:02:49 |       1.0 GB |   786.86 MB |       04:00:00 |      00:14:12 |       18.8 |     76.8 |   5.9 |
| TrimAdapterSequences_SampleName_Lane3 |    16 |       00:15:00 |      00:02:51 |       1.0 GB |   778.34 MB |       04:00:00 |      00:14:49 |       19.0 |     76.0 |   6.2 |
| TrimAdapterSequences_SampleName_Lane4 |    16 |       00:15:00 |      00:02:53 |       1.0 GB |   809.82 MB |       04:00:00 |      00:14:43 |       19.2 |     79.1 |   6.1 |
| MergeTrimmedFastqFiles_SampleName     |     1 |       00:05:00 |      00:00:33 |     128.0 MB |    752.0 KB |       00:05:00 |      00:00:18 |       11.0 |      0.6 |   6.0 |
| StarAlignment_SampleName              |    36 |       00:30:00 |      00:12:43 |      64.0 GB |    43.91 GB |       18:00:00 |      03:10:08 |       42.4 |     68.6 |  17.6 |
| StarFusion_SampleName                 |    16 |       01:00:00 |      00:37:43 |      64.0 GB |     41.2 GB |       16:00:00 |      03:59:23 |       62.9 |     64.4 |  24.9 |
+---------------------------------------+-------+----------------+---------------+--------------+-------------+----------------+---------------+------------+----------+-------+
```

The simplest way to install `gwf-utilization` is by using conda:

```
$ conda install -c micknudsen gwf-utilization
```
