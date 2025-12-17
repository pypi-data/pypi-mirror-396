use symphonia::core::audio::{AudioBuffer, AudioBufferRef, Signal};
use symphonia::core::codecs::{Decoder, DecoderOptions};
use symphonia::core::formats::{FormatReader, FormatOptions};
use symphonia::core::io::MediaSourceStream;
use symphonia::core::meta::MetadataOptions;
use symphonia::core::probe::Hint;
use anyhow::{Result, Context};
use std::fs::File;
use std::path::Path;

#[allow(dead_code)]
const BUFFER_SIZE: usize = 8192; // Smaller buffer for streaming

#[allow(dead_code)]
pub struct StreamingAudioProcessor {
    pub sample_rate: u32,
    pub channels: u16,
    format: Box<dyn FormatReader>,
    decoder: Box<dyn Decoder>,
    track_id: u32,
}

#[allow(dead_code)]
impl StreamingAudioProcessor {
    pub fn new<P: AsRef<Path>>(path: P) -> Result<Self> {
        let file = File::open(path)?;
        let media_source = MediaSourceStream::new(Box::new(file), Default::default());
        
        let hint = Hint::new();
        let meta_opts = MetadataOptions::default();
        let fmt_opts = FormatOptions::default();
        
        let probed = symphonia::default::get_probe()
            .format(&hint, media_source, &fmt_opts, &meta_opts)
            .context("Failed to probe audio format")?;
        
        let format = probed.format;
        
        let track = format.tracks()
            .iter()
            .find(|t| t.codec_params.codec != symphonia::core::codecs::CODEC_TYPE_NULL)
            .context("No audio track found")?;
        
        let track_id = track.id;
        
        let decoder_opts = DecoderOptions::default();
        let decoder = symphonia::default::get_codecs()
            .make(&track.codec_params, &decoder_opts)
            .context("Failed to create decoder")?;
        
        let sample_rate = track.codec_params.sample_rate.unwrap_or(44100);
        let channels = track.codec_params.channels.map(|ch| ch.count()).unwrap_or(2) as u16;
        
        Ok(Self {
            sample_rate,
            channels,
            format,
            decoder,
            track_id,
        })
    }
    
    pub fn process_with_callback<F>(&mut self, mut callback: F) -> Result<()>
    where
        F: FnMut(&[f64]) -> Result<()>,
    {
        loop {
            let packet = match self.format.next_packet() {
                Ok(packet) => packet,
                Err(_) => break, // End of stream
            };
            
            if packet.track_id() != self.track_id {
                continue;
            }
            
            let audio_buf = self.decoder.decode(&packet)
                .context("Failed to decode packet")?;
            
            let mut output = Vec::new();
            Self::convert_to_f64_static(&audio_buf, &mut output)?;
            
            callback(&output)?;
        }
        
        Ok(())
    }
    
    fn convert_to_f64_static(audio_buf: &AudioBufferRef, output: &mut Vec<f64>) -> Result<()> {
        
        match audio_buf {
            AudioBufferRef::F64(buf) => Self::interleave_f64_static(buf, output),
            AudioBufferRef::F32(buf) => Self::interleave_f32_static(buf, output),
            AudioBufferRef::S32(buf) => Self::interleave_i32_static(buf, output),
            AudioBufferRef::S16(buf) => Self::interleave_i16_static(buf, output),
            AudioBufferRef::U8(buf) => Self::interleave_u8_static(buf, output),
            _ => return Err(anyhow::anyhow!("Unsupported audio format")),
        }
        
        Ok(())
    }
    
    fn interleave_f64_static(buf: &AudioBuffer<f64>, output: &mut Vec<f64>) {
        let num_channels = buf.spec().channels.count();
        let num_samples = buf.capacity();
        
        output.clear();
        output.reserve(num_channels * num_samples);
        
        for frame in 0..num_samples {
            for ch in 0..num_channels {
                let channel = buf.chan(ch);
                output.push(channel[frame]);
            }
        }
    }
    
    fn interleave_f32_static(buf: &AudioBuffer<f32>, output: &mut Vec<f64>) {
        let num_channels = buf.spec().channels.count();
        let num_samples = buf.capacity();
        
        output.clear();
        output.reserve(num_channels * num_samples);
        
        for frame in 0..num_samples {
            for ch in 0..num_channels {
                let channel = buf.chan(ch);
                output.push(channel[frame] as f64);
            }
        }
    }
    
    fn interleave_i32_static(buf: &AudioBuffer<i32>, output: &mut Vec<f64>) {
        let num_channels = buf.spec().channels.count();
        let num_samples = buf.capacity();
        
        output.clear();
        output.reserve(num_channels * num_samples);
        
        for frame in 0..num_samples {
            for ch in 0..num_channels {
                let channel = buf.chan(ch);
                output.push(channel[frame] as f64 / i32::MAX as f64);
            }
        }
    }
    
    fn interleave_i16_static(buf: &AudioBuffer<i16>, output: &mut Vec<f64>) {
        let num_channels = buf.spec().channels.count();
        let num_samples = buf.capacity();
        
        output.clear();
        output.reserve(num_channels * num_samples);
        
        for frame in 0..num_samples {
            for ch in 0..num_channels {
                let channel = buf.chan(ch);
                output.push(channel[frame] as f64 / i16::MAX as f64);
            }
        }
    }
    
    fn interleave_u8_static(buf: &AudioBuffer<u8>, output: &mut Vec<f64>) {
        let num_channels = buf.spec().channels.count();
        let num_samples = buf.capacity();
        
        output.clear();
        output.reserve(num_channels * num_samples);
        
        for frame in 0..num_samples {
            for ch in 0..num_channels {
                let channel = buf.chan(ch);
                let normalized = (channel[frame] as f64 - 128.0) / 127.0;
                output.push(normalized);
            }
        }
    }
}