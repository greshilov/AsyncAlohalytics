#include "3party/Alohalytics/src/event_base.h"

#include <sstream>
#include <utility>
#include <iostream>

#include <boost/python.hpp>
#include <vector>

namespace py = boost::python;
using namespace alohalytics;


// Converts a C++ vector to a python list
template <class T>
py::list ToPythonList(std::vector<T> vector) {
    typename std::vector<T>::iterator iter;
    py::list list;
    for (iter = vector.begin(); iter != vector.end(); ++iter) {
        list.append(*iter);
    }
    return list;
}

struct AlohaEvent {
  uint64_t timestamp;
  std::string key;
  std::string value;
  std::string location;

  void flush() {
    this->timestamp = 0;
    this->key = "";
    this->value = "";
    this->location = "";
  }

  void load(AlohalyticsKeyValueLocationEvent const* event) {
    this->timestamp = event->timestamp / 1000;
    this->key = event->key;
    this->value = event->value;
    this->location = event->location.Encode();
  }

  void load(AlohalyticsKeyLocationEvent const* event) {
    this->timestamp = event->timestamp / 1000;
    this->key = event->key;
    this->location = event->location.Encode();
  }

  void load(AlohalyticsKeyValueEvent const* event) {
    this->timestamp = event->timestamp / 1000;
    this->key = event->key;
    this->value = event->value;
  }

  void load(AlohalyticsKeyEvent const* event) {
    this->timestamp = event->timestamp / 1000;
    this->key = event->key;
  }
};


py::tuple decode(std::string const& body)
{
  std::vector<AlohaEvent> events;
  std::string alohaId;

  std::istringstream in_stream(body);
  cereal::BinaryInputArchive in_ar(in_stream);
  std::ostringstream out_stream;

  std::unique_ptr<AlohalyticsBaseEvent> ptr;

  const std::streampos bytes_to_read = body.size();

  AlohaEvent event;

  while (bytes_to_read > in_stream.tellg()) {
    in_ar(ptr);
    event.flush();

    if (!ptr) {
      throw std::invalid_argument("Corrupted Cereal object, this == 0.");
    }
    const AlohalyticsIdEvent * id_event = dynamic_cast<const AlohalyticsIdEvent *>(ptr.get());
    if (id_event) {
      alohaId = id_event->id;
    } else {

      AlohalyticsKeyValueLocationEvent const * kvl_ev = dynamic_cast<const AlohalyticsKeyValueLocationEvent *>(ptr.get());
      if (kvl_ev) {
        event.load(kvl_ev);
        events.push_back(event);
        continue;
      }

      AlohalyticsKeyLocationEvent const * kl_ev = dynamic_cast<const AlohalyticsKeyLocationEvent *>(ptr.get());
      if (kl_ev) {
        event.load(kl_ev);
        events.push_back(event);
        continue;
      }

      AlohalyticsKeyValueEvent const * kv_ev = dynamic_cast<const AlohalyticsKeyValueEvent *>(ptr.get());
      if (kv_ev) {
        event.load(kv_ev);
        events.push_back(event);
        continue;
      }
      AlohalyticsKeyEvent const * k_ev = dynamic_cast<const AlohalyticsKeyEvent *>(ptr.get());
      if (k_ev) {
        event.load(k_ev);
        events.push_back(event);
      }
    }
  }
  return py::make_tuple(alohaId, ToPythonList<AlohaEvent>(events));
}

BOOST_PYTHON_MODULE(pyalohareciever)
{
    using namespace boost::python;

    class_<AlohaEvent>("AlohaEvent")
      .add_property("timestamp", &AlohaEvent::timestamp)
      .add_property("key", &AlohaEvent::key)
      .add_property("value", &AlohaEvent::value)
      .add_property("location", &AlohaEvent::location)
    ;

    def("decode", decode);
}
