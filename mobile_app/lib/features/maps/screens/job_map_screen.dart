import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../core/models/job.dart';

class JobMapScreen extends StatefulWidget {
  final List<Job> jobs;
  final Job? selectedJob;

  const JobMapScreen({
    super.key,
    required this.jobs,
    this.selectedJob,
  });

  @override
  State<JobMapScreen> createState() => _JobMapScreenState();
}

class _JobMapScreenState extends State<JobMapScreen> {
  final Completer<GoogleMapController> _controller = Completer();
  Set<Marker> _markers = {};
  Position? _currentPosition;
  Job? _selectedJob;

  static const CameraPosition _defaultPosition = CameraPosition(
    target: LatLng(51.5074, -0.1278), // London default
    zoom: 10,
  );

  @override
  void initState() {
    super.initState();
    _selectedJob = widget.selectedJob;
    _getCurrentLocation();
    _buildMarkers();
  }

  Future<void> _getCurrentLocation() async {
    try {
      final permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        await Geolocator.requestPermission();
      }
      
      _currentPosition = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      
      if (mounted) {
        setState(() {});
        _fitBounds();
      }
    } catch (e) {
      // Location not available
    }
  }

  void _buildMarkers() {
    final markers = <Marker>{};
    
    for (final job in widget.jobs) {
      if (job.latitude != null && job.longitude != null) {
        markers.add(
          Marker(
            markerId: MarkerId('job_${job.id}'),
            position: LatLng(job.latitude!, job.longitude!),
            infoWindow: InfoWindow(
              title: job.name,
              snippet: job.fullAddress,
              onTap: () => _selectJob(job),
            ),
            icon: BitmapDescriptor.defaultMarkerWithHue(
              _getMarkerHue(job.status),
            ),
            onTap: () => _selectJob(job),
          ),
        );
      }
    }
    
    setState(() => _markers = markers);
  }

  double _getMarkerHue(String status) {
    switch (status) {
      case 'completed':
        return BitmapDescriptor.hueGreen;
      case 'in_progress':
        return BitmapDescriptor.hueBlue;
      case 'pending':
      case 'assigned':
        return BitmapDescriptor.hueOrange;
      case 'cancelled':
        return BitmapDescriptor.hueRed;
      default:
        return BitmapDescriptor.hueRed;
    }
  }

  void _selectJob(Job job) {
    setState(() => _selectedJob = job);
  }

  Future<void> _fitBounds() async {
    if (_markers.isEmpty) return;
    
    final controller = await _controller.future;
    
    double minLat = 90, maxLat = -90, minLng = 180, maxLng = -180;
    
    for (final marker in _markers) {
      minLat = marker.position.latitude < minLat ? marker.position.latitude : minLat;
      maxLat = marker.position.latitude > maxLat ? marker.position.latitude : maxLat;
      minLng = marker.position.longitude < minLng ? marker.position.longitude : minLng;
      maxLng = marker.position.longitude > maxLng ? marker.position.longitude : maxLng;
    }
    
    if (_currentPosition != null) {
      minLat = _currentPosition!.latitude < minLat ? _currentPosition!.latitude : minLat;
      maxLat = _currentPosition!.latitude > maxLat ? _currentPosition!.latitude : maxLat;
      minLng = _currentPosition!.longitude < minLng ? _currentPosition!.longitude : minLng;
      maxLng = _currentPosition!.longitude > maxLng ? _currentPosition!.longitude : maxLng;
    }
    
    controller.animateCamera(
      CameraUpdate.newLatLngBounds(
        LatLngBounds(
          southwest: LatLng(minLat, minLng),
          northeast: LatLng(maxLat, maxLng),
        ),
        50,
      ),
    );
  }

  Future<void> _navigateToJob(Job job) async {
    if (job.latitude == null || job.longitude == null) return;
    
    final url = Uri.parse(
      'https://www.google.com/maps/dir/?api=1&destination=${job.latitude},${job.longitude}',
    );
    
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Job Map'),
        actions: [
          IconButton(
            icon: const Icon(Icons.my_location),
            onPressed: _fitBounds,
          ),
        ],
      ),
      body: Stack(
        children: [
          GoogleMap(
            mapType: MapType.normal,
            initialCameraPosition: _defaultPosition,
            markers: _markers,
            myLocationEnabled: true,
            myLocationButtonEnabled: false,
            onMapCreated: (controller) {
              _controller.complete(controller);
              _fitBounds();
            },
          ),
          if (_selectedJob != null)
            Positioned(
              left: 16,
              right: 16,
              bottom: 16,
              child: _buildJobCard(_selectedJob!),
            ),
        ],
      ),
    );
  }

  Widget _buildJobCard(Job job) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(job.name, style: Theme.of(context).textTheme.titleMedium),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => setState(() => _selectedJob = null),
                ),
              ],
            ),
            Text(job.fullAddress, style: Theme.of(context).textTheme.bodySmall),
            const SizedBox(height: 8),
            Row(
              children: [
                Chip(label: Text(job.statusLabel)),
                const Spacer(),
                ElevatedButton.icon(
                  onPressed: () => _navigateToJob(job),
                  icon: const Icon(Icons.directions),
                  label: const Text('Navigate'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

