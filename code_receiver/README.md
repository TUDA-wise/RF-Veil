# RF-Veil Receiver Code

This folder contains the sub-VIs we used to implement the **RF-Veil receiver**. We integrated the code into the existing NI 802.11 AFW code [1].

We implemented most of the logic on the host. The *VI 802.11 Prepare Channel Estimation ac* pulls a fresh set of CSI from the FPGA to update the plots on the host panel of the 802.11 AFW every 250 milliseconds inside a loop.  The VI reads the *Channel Estimation FIFO*, containing 1 or multiple sets of 256 complex-valued samples, obtained from the channel estimation on the physical layer. Each of the 256 complex values per measurement represent one sample per subcarrier. The complex value of each subcarrier gets separated into amplitude and phase and joined with the frequency offset index to eventually form an array of clusters. The plot *Channel Estimation* finally displays this array of clusters.

In order to implement the RF-Veil Receiver on top of the NI 802.11 AFW, use the VI **TODO** and put it into a separate loop in the *Host* VI. It is then executed back to back. Note that, in order to get a better real-time performance, i.e. execute the RF-Veil Receiver on every received frame, the code inside this VI needs to be pushed to the lower MAC or PHY layer on the FPGA. 

## Implementation Details

Due to NI AFW licensing, we are only able to share the code we wrote on our own. Hence, this repository only contains code-snippets and does not represent a fully-functional 802.11 station. In order to use this PoC, the VIs have to be built into the 802.11 AFW.

In the *802.11 Host.gvi*, the *802.11 Prepare Channel Estimation.gvi* has to be exchanged with the *802.11 Prepare Channel Estimation ac.gvi* which already filters for 802.11ac measurements. In order to increase the sampling time, the VI has to be placed in a loop on its own. It already calls all the requires sub-VIs which handle the fingerprint extraction. In order to see the received fingerprints in real-time, open the panel-view of the *RT ident of Rogue 802.11ac.gvi* VI. When the AFW is running and receiving frames, the diagrams show different stages of the fingerprint extraction (phase unwrapping, normalization, etc.). For the receiver, no changes to the FPGA image is required. 


[1] https://www.ni.com/de-de/shop/software/products/labview-communications-802-11-application-framework.html
