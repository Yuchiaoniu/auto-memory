#!/bin/bash
cd ~/forest-carbon-measurement
LOG=~/p4_v2.log
: > "$LOG"
run() {
  echo "" | tee -a "$LOG"
  echo "########## $2 (tape $3) ##########" | tee -a "$LOG"
  stdbuf -oL -eL node rerun_p4.js --file-id "$1" --img "$2" --tape "$3" --repeat 10 2>&1 | tee -a "$LOG"
}
run 1lpkf7TYbWLylUKtG0ABFdZDitkW2T0wN IMG_5786 22.6
run 13fgOJO--W4opami5ZVKoqIl7Nxk-Ec6F IMG_5787 27.2
run 1F0437umBsIGv_-oetcpKQokZW9KSXjcp IMG_5788 27.7
run 1LLyAp4BjgjwX5cPHdP42rmasGPcZSycH IMG_5789 26.3
run 1HrK9Iz2h2PqyeyC1b1rLvFipP6jpwD-P IMG_5790 19.4
run 1fFNvMJSiDo6h0cGK7VBfDW7_Q9pE7aL4 IMG_5791 30.2
run 1oFUNweQ1E2BCJRuuEFgATXYRUV5rWzON IMG_5792 28.6
run 1ZVDRkpkw0M7RYwS03Fdf19pAJKT4AnZ5 IMG_5793 33.7
run 1vk4A2WYgoGBxN581kf5H3vshPOimerGj IMG_5794 31.2
run 1mAsxJchl2JRrYMyxSWBz8yRzTTvNpDmD IMG_5795 22.0
run 1-yXWP7XWpgTeZBDQC9sHyOpIxljxm_tH IMG_5798 42.0
run 19hdCOLZKBOLf1F3rtZ1LLeukXUw2NAFy IMG_5799 43.6
run 1yvo9_vja1TJOFl8TTiHQDHi9vMNbRfTf IMG_5800 17.5
run 1vwIqBt4Zob3wno3999dgfQkF5SSggRi6 IMG_5801 16.9
run 1lVacWtaNhrMq3oM2cfOgWYa7namSLlrK IMG_5802 43.9
run 1U3Mi5Gtu_BqsYV2CjAyVQB4wy6J2ZbAu IMG_5803 43.0
run 1z1kzhPx4kUOj6opGt4ZILyawIQjcSvyp IMG_5805 35.7
run 1ybyFmKlFRx3kuNFVSNYJBP4dMa2KfcL7 IMG_5806 38.8
run 1EbJkGAZpmb9CbMm0YlnKQhqEKaJ9olzB IMG_5807 31.5
run 1Kzcy00bGk-kZjL8lQQ66wD1v-OZkOgAb IMG_5808 31.8
run 1DY1OV8PEPjR3XGIcyVne1AtO1QdpUHUF IMG_5809 30.6
run 1v6BthyaAo0uY4HvIs-yK5_YETJnWSV-5 IMG_5810 29.9
run 1CgeLGT-k2NiW54MXdInjuI5OAlYsTlf5 IMG_5811 30.6
run 1cbNBVVyqf0M0ShepbWT230yF4bddN4yA IMG_5812 30.9
run 1e5CytcJRc7XhbdK_j0UWuUiYkH6YqKrD IMG_5813 26.1
run 1DgPf1kPfqynAWSJBY44XM65dVkeLross IMG_5814 38.5
run 1hAJOWC6SO9urNIn0aLESVQ7u1JUfZeHT IMG_5815 32.5
run 1MYhIVJI2SBkbpAZFBoq7OdJgA4N5pog6 IMG_5817 24.5
run 13qfRS4GWJvWL-ur4F54pndHzsCTl5a9H IMG_5818 17.5
run 1dFF4DF0JVlZqgxCQeOSxMSvnlybOCOfn IMG_5819 21.6
echo "" | tee -a "$LOG"
echo "=== ALL V2 DONE ===" | tee -a "$LOG"
