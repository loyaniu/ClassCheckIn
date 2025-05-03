# ClassCheckIn

> Done by Zhonglin Niu (zn23), and Yuese Li (yl77).

"ClassCheckIn uses Raspberry Pi and a camera to instantly recognize students by their face as they enter class, automating attendance with just one photo per student."

## How to run

1. Copy the `.env.local.sample` file to `.env.local` and fill in the required variables.
2. Copy the `face_recognition/.env.sample` file to `face_recognition/.env` and fill in the required variables.
3. On local machine, run the following commands in the root directory (I used `python3.12`):

   ```bash
   cd class-checkin
   python3 -m venv venv
   source venv/bin/activate
   pip install -r face-recognition/requirements.txt
   npm install
   npm run dev
   ```

4. On the Raspberry Pi, run the following commands:

   ```bash
   cd RPI
   python3 cam_capture.py
   python3 mqtt_client.py
   ```

## Inspiration

We were frustrated with time-consuming attendance methods like scanning QR codes, logging into Moodle, or professors calling roll. We wanted to create a seamless attendance system that wouldn't disrupt valuable class time.

## What it does

ClassCheckIn uses facial recognition to automatically mark students present as they enter the classroom.

## How we built it

We developed the web interface using React+Vite, captured video streams from a Raspberry Pi camera, and implemented Python-based facial recognition that sends data to a cloud database for the web interface.

## Challenges we ran into

- Due to the Raspberry Pi's limited memory (1GB), facial recognition had to be performed locally
- Optimizing facial recognition speed while maintaining accuracy
- Implementing reliable MQTT communication between components for real-time feedback
- Integrating multiple systems (web interface, recognition engine, and hardware feedback) into a cohesive solution

## Accomplishments that we're proud of

Our system confirms successful recognition through visual and audio feedback - green LED flashes and short buzzer sounds via MQTT protocol. The entire recognition process takes less than one second, and all attendance data is securely stored in our cloud database.

## What we learned

Working on ClassCheckIn taught us how to integrate hardware and software components seamlessly. We gained valuable experience in facial recognition algorithms, real-time data processing, and creating responsive user interfaces. The project also strengthened our skills in database management and IoT communication protocols, particularly MQTT for device coordination.

## What's next for ClassCheckIn

We plan to enhance our database architecture to enable professors to track student attendance throughout an entire semester and export the data for their records.
