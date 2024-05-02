import 'dart:async';
// import 'dart:ffi';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:sensors/sensors.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:permission_handler/permission_handler.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:socket_io_client/socket_io_client.dart' as SocketIO;
import 'package:shared_preferences/shared_preferences.dart';

List<CameraDescription> cameras = [];
FlutterTts flutterTts = FlutterTts();
String ipAddress = "";
int portNumber = -1;
double ICPS = 0.0;

bool _isRecording = false;
bool __isListening = false;

Future<void> main() async {
  // Ensure that plugin services are initialized
  WidgetsFlutterBinding.ensureInitialized();
  SharedPreferences prefs = await SharedPreferences.getInstance();
  ipAddress = (await prefs.getString('ip') ?? "").toString();
  portNumber = int.parse((await prefs.getInt('port') ?? -1).toString());
  ICPS = double.parse((await prefs.getDouble('icps') ?? 0.0).toString());
  // Available pref
  cameras = await availableCameras();

  // Run app
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: CameraApp(),
    );
  }
}

class ConnectionInputPage extends StatefulWidget {
  @override
  _ConnectionInputPageState createState() => _ConnectionInputPageState();
}

class _ConnectionInputPageState extends State<ConnectionInputPage> {
  final TextEditingController _ipController = TextEditingController();
  final TextEditingController _portController = TextEditingController();
  final TextEditingController _numberController = TextEditingController();
  final TextEditingController _secondsController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Initializing configurations'),
      ),
      body: Form(
        key: _formKey,
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              TextFormField(
                controller: _ipController,
                decoration: InputDecoration(
                  labelText: 'IP Address',
                  hintText: 'Enter registered instance IP',
                ),
                validator: (value) {
                  if (value != null && value.isEmpty) {
                    if (!RegExp(r'^(\d{1,3}\.){3}\d{1,3}$').hasMatch(value)) {
                      return 'IP address is not valid';
                    } else
                      return 'Please enter an IP address';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16.0),
              TextFormField(
                controller: _portController,
                decoration: InputDecoration(
                  labelText: 'Port',
                  hintText: 'Enter port number',
                ),
                validator: (value) {
                  if (value != null && value.isEmpty) {
                    if (!RegExp(r'^\d+$').hasMatch(value) ||
                        int.tryParse(value)! > 65535) {
                      return 'Port number is not valid or in range';
                    } else {
                      return 'Please enter a port number';
                    }
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16.0),
              TextFormField(
                controller: _numberController,
                decoration: const InputDecoration(
                  labelText: 'ICPS Image count',
                  hintText: 'Enter a number',
                ),
                validator: (value) {
                  if (value != null && value.isEmpty) {
                    if (!RegExp(r'^\d+$').hasMatch(value)) {
                      return 'Seconds count is not valid';
                    } else {
                      return 'Please enter a number';
                    }
                  }
                  return null;
                },
              ),
              SizedBox(height: 16.0),
              TextFormField(
                controller: _secondsController,
                decoration: InputDecoration(
                  labelText: 'ICPS seconds count',
                  hintText: 'Enter a number',
                ),
                validator: (value) {
                  if (value != null && value.isEmpty) {
                    if (!RegExp(r'^\d+$').hasMatch(value)) {
                      return 'seconds count is not valid number';
                    } else
                      return 'Please enter a number';
                  }
                  return null;
                },
              ),
              SizedBox(height: 24.0),
              ElevatedButton(
                onPressed: () async {
                  // Validate returns true if the form is valid, otherwise false.
                  if (_formKey.currentState!.validate()) {
                    // If the form is valid, display a Snackbar.
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Processing Data')),
                    );

                    await setStringPreference('ip', _ipController.text);
                    await setIntPreference(
                        'port', int.parse(_portController.text));
                    double ICPSRes = double.parse(_secondsController.text) /
                        double.parse(_numberController.text);

                    await setDoublePreference('icps', ICPSRes);
                    await initializeVariables();
                    Navigator.pop(context);
                  }
                },
                child: Text('Connect'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _ipController.dispose();
    _portController.dispose();
    _numberController.dispose();
    _secondsController.dispose();
    super.dispose();
  }
}

Future<String?> getStringPreference(String key) async {
  final SharedPreferences prefs = await SharedPreferences.getInstance();
  return prefs.getString(key);
}

Future<int?> getIntPreference(String key) async {
  final SharedPreferences prefs = await SharedPreferences.getInstance();
  return prefs.getInt(key);
}

Future<double?> getDoublePreference(String key) async {
  final SharedPreferences prefs = await SharedPreferences.getInstance();
  return prefs.getDouble(key);
}

Future<void> setStringPreference(String key, String value) async {
  final SharedPreferences prefs = await SharedPreferences.getInstance();
  prefs.setString(key, value);
}

Future<void> setIntPreference(String key, int value) async {
  final SharedPreferences prefs = await SharedPreferences.getInstance();
  prefs.setInt(key, value);
}

Future<void> setDoublePreference(String key, double value) async {
  final SharedPreferences prefs = await SharedPreferences.getInstance();
  prefs.setDouble(key, value);
}

Future<String?> checkInstance(String name) async {
  final prefs = await SharedPreferences.getInstance();
  return prefs.getString(name);
}

Future<void> SaveInstance(String name, String value) async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString(name, value);
}

Future<void> initializeVariables() async {
  ipAddress = await getStringPreference('ip') ?? "";
  portNumber = await getIntPreference('port') ?? -1;
  ICPS = await getDoublePreference('icps') ?? 0.0;
}

class TextToSpeechService {
  late FlutterTts flutterTts;
  bool _isSpeaking = false;

  TextToSpeechService() {
    flutterTts = FlutterTts();
    _initializeTts();
    flutterTts.setStartHandler(() {
      _isSpeaking = true;
    });

    flutterTts.setCompletionHandler(() {
      _isSpeaking = false;
    });

    flutterTts.setErrorHandler((msg) {
      _isSpeaking = false;
    });
  }

  void _initializeTts() async {
    await flutterTts.setLanguage("en-US");
    await flutterTts.setPitch(1.0);
    await flutterTts.setVolume(1.0);
    await flutterTts.setSpeechRate(0.5); // Adjust the speech rate as needed
  }

  Future<void> speak(String text) async {
    if (_isSpeaking) {
      await flutterTts.stop(); // Stop current speech before starting a new one
    }
    await flutterTts.speak(text);
  }

  bool get isSpeaking => _isSpeaking;
}

class CameraApp extends StatefulWidget {
  const CameraApp({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _CameraAppState createState() => _CameraAppState();
  static _CameraAppState? of(BuildContext context) {
    return context.findAncestorStateOfType<_CameraAppState>();
  }
}

class _CameraAppState extends State<CameraApp> {
  late CameraController controller;
  GyroscopeEvent? _gyroscopeEvent;
  StreamSubscription<GyroscopeEvent>? _gyroscopeSubscription;
  // WebSocketChannel? channel; // Add this line
  SocketIO.Socket? socket;
  FlutterSoundRecorder? _audioRecorder;
  final stt.SpeechToText _speechToText = stt.SpeechToText();
  @override
  void initState() async{
    super.initState();
  SharedPreferences prefs = await SharedPreferences.getInstance();
  ipAddress = (await prefs.getString('ip') ?? "").toString();
  portNumber = int.parse((await prefs.getInt('port') ?? -1).toString());
  ICPS = double.parse((await prefs.getDouble('icps') ?? 0.0).toString());
    // channel = WebSocketChannel.connect(
    //   Uri.parse(
    //       'ws://$ipAddress:$portNumber/socket.io/?transport=websocket'), // Use the same port as your HTTP server
    // );
    // if (ipAddress.isEmpty || portNumber.isNegative || ICPS == 0.0) {
    //   Navigator.of(context).push(
    //     MaterialPageRoute(builder: (context) => ConnectionInputPage()),
    //   );
    // }
    print('$ipAddress pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp');
    socket = SocketIO.io('http://$ipAddress:$portNumber', <String, dynamic>{
      'transports': ['websocket'],
    });
    controller = CameraController(cameras[0], ResolutionPreset.medium);
    controller.initialize().then((_) {
      if (!mounted) return;
      setState(() {});
      // if (ipAddress.isNotEmpty && !portNumber.isNegative && ICPS != 0.0) {
      // Start listening to gyroscope events
      startImageStream();
      _gyroscopeSubscription = gyroscopeEvents.listen((GyroscopeEvent event) {
        _gyroscopeEvent = event;
      });

      socket?.onConnect((_) {
        // If the form is valid, display a Snackbar.
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Connected successfully....')),
        );
        socket?.emit('message', 'Hello from Flutter');
      });
      socket?.onConnectError((data) {
        // If the form is valid, display a Snackbar.
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Errorjust" + data)),
        );
      });

      // Handle connection timeout
      socket?.onConnectTimeout((_) {
        // If the form is valid, display a Snackbar.
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('connection timedout....')),
        );
      });
      socket?.onDisconnect((_) =>
          // If the form is valid, display a Snackbar.
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Server disconnected....')),
          ));

      // Listen to incoming messages
      // channel?.stream.listen((message) {
      //   print(message);
      //   onTextDataReceived(message);
      // });
      socket?.on('message', (data) {
        onTextDataReceived(data);
      });
      // Initialize the audio recorder
      _initAudioRecorder();
      // }
    });
  }

  void startAudioRecording() async {
    await _audioRecorder?.startRecorder(toFile: 'audio.aac');
    setState(() {
      _isRecording = true;
    });
  }

  void stopAudioRecording() async {
    await _audioRecorder?.stopRecorder();
    setState(() {
      _isRecording = false;
    });
    sendAudioFile(
        'audio.aac'); // Replace with the path where audio file is saved
  }

  void startListening() async {
    await Permission.microphone.request();
    await _speechToText.initialize();
    _speechToText.listen(onResult: (result) {
      // Do something with the text
      sendTextData(result.recognizedWords);
    });
    setState(() {
      __isListening = true;
    });
  }

  void stopListening() {
    _speechToText.stop();
    setState(() {
      __isListening = false;
    });
  }

  void sendAudioFile(String audioFilePath) async {
    // Implement logic to send audio file to server
  }

  void sendTextData(String text) async {
    socket?.emit('message', text);
  }

  void _initAudioRecorder() async {
    await Permission.microphone.request();
    _audioRecorder = FlutterSoundRecorder();
    await _audioRecorder?.openRecorder();
  }

  void onTextDataReceived(dynamic message) {
    final ttsService = TextToSpeechService();
    // ttsService._initializeTts();
    ttsService.speak(message);
    // Handle incoming text data sent from the Flask server via WebSocke
    // print('Text data received from WebSocket: $message');
  }

  void startImageStream() async {
    int durationicps = (ICPS * 1000.0).toInt();
    var frequency = Duration(milliseconds: durationicps); // 2 photos per second
    // Make sure the controller is initialized and streaming images
    if (controller.value.isInitialized) {
      Timer.periodic(frequency, (timer) async {
        try {
          // Attempt to take a picture
          XFile tempImage = await controller.takePicture();
          // Send the picture to the Flask server
          sendImage(tempImage.path);
        } catch (e) {
          print(e); // Handle the error
        }
      });
    }
  }

  void sendImage(String imagePath) async {
    var uri = Uri.parse('http://$ipAddress:$portNumber/upload-image');
    print("$ipAddress  :   $portNumber");
    var request = http.MultipartRequest('POST', uri);
    request.files.add(await http.MultipartFile.fromPath('image', imagePath));

    // Attach the gyroscope data if available
    if (_gyroscopeEvent != null) {
      request.fields['gyroscope_x'] = _gyroscopeEvent!.x.toString();
      request.fields['gyroscope_y'] = _gyroscopeEvent!.y.toString();
      request.fields['gyroscope_z'] = _gyroscopeEvent!.z.toString();
    }
    await request.send();
    // var response = await request.send();
    // Optionally delete the image file if you no longer need it
  }

  @override
  Widget build(BuildContext context) {
    if (!controller.value.isInitialized) {
      // Navigator.of(context).push(
      //   MaterialPageRoute(builder: (context) => ConnectionInputPage()),
      // );
      return Container();
    }

    return Scaffold(
        appBar: AppBar(
          title: const Text("Ear vision"),
        ),
        body: Column(
          children: <Widget>[
            Container(
              height: 400,
              child: AspectRatio(
                aspectRatio: controller.value.aspectRatio,
                child: CameraPreview(controller),
              ),
            ),
            Container(
              height: 50,
            ),
            Center(
              child: Text("IP Address: " + ipAddress.toString()),
            ),
            Container(height: 25),
            Center(
              child: Text("Port Number: " + portNumber.toString()),
            ),
            Container(height: 25),
            Center(
              child: Text("ICPS: " + ICPS.toString()),
            ),
            Container(height: 25),
            SpeechToTextButton(),
            Container(height: 50)
          ],
        ),
        floatingActionButton: Padding(
          padding: const EdgeInsets.only(bottom: 50.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.end,
            children: <Widget>[
              // FloatingActionButton(
              //   onPressed: () {
              //     socket?.emit('message', 'Hello from Flutter');
              //   },
              //   tooltip: 'Send message',
              //   child: Icon(Icons.send),
              // ),
              FloatingActionButton(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                        builder: (context) => ConnectionInputPage()),
                  );
                },
                tooltip: 'Configure',
                child: Icon(Icons.settings),
              ),
              // IconButton(
              //   icon: Icon(Icons.mic),
              //   tooltip: 'Configure',
              //   onPressed: () {},
              // ),
            ],
          ),
        ));
  }

  @override
  void dispose() {
    socket?.dispose();
    controller.dispose();
    _gyroscopeSubscription?.cancel(); // Cancel the gyroscope subscription
    super.dispose();
  }
}

class SpeechToTextButton extends StatefulWidget {
  @override
  _SpeechToTextButtonState createState() => _SpeechToTextButtonState();
}

class _SpeechToTextButtonState extends State<SpeechToTextButton> {
  stt.SpeechToText _speechToText = stt.SpeechToText();
  bool _isListening = false;

  @override
  void initState() {
    super.initState();
    _speechToText = stt.SpeechToText();
  }

  // SocketIO.Socket socket =
  //     SocketIO.io('http://$ipAddress:$portNumber', <String, dynamic>{
  //   'transports': ['websocket'],
  // });
  late final CameraApp cameraApp;
  void _startListening() async {
    final available = await _speechToText.initialize();
    if (available) {
      setState(() => _isListening = true);
      _speechToText.listen(onResult: (result) {
        // Handle your result in real-time
        // if (!socket.connected) {
        //   socket.onConnect((_) {
        //     socket.emit(result.toString());
        //   });
        // } else
        //   socket.emit(result.toString());
        // sendTextData();
        sendAudioRecord(result.recognizedWords.toString());
        print(result.recognizedWords);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(result.recognizedWords.toString())),
        );
      });
    }
  }

  Future<void> sendAudioRecord(String text) async {
    var uri = Uri.parse('http://$ipAddress:$portNumber/Speach_cmd');
    print("$ipAddress  :   $portNumber");
    var request = http.MultipartRequest('POST', uri);
    request.fields['speach_cmd'] = text;
    await request.send();
  }

  void _stopListening() {
    _speechToText.stop();
    setState(() => _isListening = false);
    // Handle any post-processing or final text display here
    // after _speechToText has stopped listening.
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
        onLongPress: _startListening,
        onLongPressUp: _stopListening,
        child: Container(
          decoration: BoxDecoration(
            color: Color.fromARGB(255, 138, 224, 235), // Replace with your desired background color
            borderRadius: BorderRadius.circular(
                25), // Replace with your desired border radius
          ),
          child: IconButton(
            icon: Icon(_isListening ? Icons.mic : Icons.mic_none),
            tooltip: 'Press and Hold to Talk',
            color: Color.fromARGB(255, 1, 32, 30), // Replace with your desired icon color
            iconSize: 50, // Replace with your desired icon size
            onPressed: () {
              // Add your logic for the regular button press here
            },
          ),
        ));
  }

  @override
  void dispose() {
    _speechToText.stop();
    super.dispose();
    // socket.dispose();
  }
}
